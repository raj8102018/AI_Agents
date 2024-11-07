"""
This module contains data preprocessing related logic
"""
# src/data_preprocessing.py
import os
import pandas as pd  # pylint: disable=import-error # type: ignore
import tensorflow as tf  # pylint: disable=import-error #os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import spacy  # type: ignore # pylint: disable=import-error
from transformers import BertTokenizer, TFBertForSequenceClassification


# Load pre-trained BERT tokenizer and model
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = TFBertForSequenceClassification.from_pretrained(
    "bert-base-uncased", num_labels=3
)  # 3 labels: cold, warm, hot

# Load spaCy model
nlp = spacy.load("en_core_web_sm")


def spacy_preprocess(text):
    """Preprocess text using spaCy."""
    words = nlp(text.lower())
    words = [word.text for word in words if word.text.isalnum()]
    return " ".join(words)

def preprocess_data(file_to_process,processed_file):
    """Clean and preprocess data from 'file to process' and save to output_file."""
    try:
        df = pd.read_csv(file_to_process)
        print(f"Original Data Shape: {df.shape}")

        # Perform data cleaning and preprocessing
        df["Name"] = df["First Name"] + " " + df["Last Name"]
        first_col = df.pop("Name")
        df.insert(0, "Name", first_col)
        df = df.drop(
            [
                "Address Street",
                "Country",
                "Zip Code",
                "Contact Number",
                "City",
                "State",
                "First Name",
                "Last Name",
            ],
            axis=1,
        )
        df["processed job_title"] = df["Job Title"].apply(spacy_preprocess)
        df["processed Company_name"] = df["Company"].apply(spacy_preprocess)
        df["processed Industry_name"] = df["Industry"].apply(spacy_preprocess)

        hot_industries = [
            "IT Services And IT Consulting",
            "Software Development",
            "Medical Device",
            "Pharmaceuticals",
            "Business Consulting And Services",
            "Hospitals And Health Care",
        ]
        warm_industries = [
            "Health, Wellness & Fitness",
            "Nonprofit Organizations",
            "Government Administration",
            "Manufacturing",
            "Appliances, Electrical, And Electronics Manufacturing",
        ]
        cold_industries = [
            "Retail",
            "Environmental Services",
            "Design Services",
            "Wholesale",
        ]

        hot_job_titles = [
            "Chief Executive Officer",
            "President",
            "Founder",
            "Vice President",
            "Director",
        ]
        warm_job_titles = [
            "Executive Director",
            "Managing Director",
            "Owner",
            "General Manager", 
            "Vice President of Operations",
        ]
        cold_job_titles = ["CoOwner", "Deputy Director", "Executive Vice President"]

        def classify_lead(row):
            """
            function that returns the lead after classifying it into one of the three categories
            """
            # Initialize the result to "Cold" by default
            result = "Cold"

            if row["Job Title"] in hot_job_titles:
                if row["Industry"] in hot_industries:
                    result = "Hot"
                elif row["Industry"] in warm_industries or row["Industry"] in cold_industries:
                    result = "Warm"
            elif row["Job Title"] in warm_job_titles:
                if row["Industry"] in warm_industries:
                    result = "Warm"
                elif row["Industry"] in hot_industries:
                    result = "Warm"
                elif row["Industry"] in cold_industries:
                    result = "Warm"
            elif row["Job Title"] in cold_job_titles:
                if row["Industry"] in hot_industries:
                    result = "Warm"
            return result

        df["lead_type"] = df.apply(classify_lead, axis=1)

        lead_type_mapping = {"Hot": 2, "Warm": 1, "Cold": 0}
        df["lead_label"] = df["lead_type"].map(lead_type_mapping)
        df = df[
            [
                "Name",
                "processed job_title",
                "processed Industry_name",
                "lead_type",
                "lead_label",
            ]
        ]

        # Save the cleaned data
        df.to_csv(processed_file, index=False)
        print(f"Processed Data Shape: {df.shape}")
        print(f"Data successfully saved to {processed_file}")

    except Exception as e: # pylint: disable=broad-except
        print(f"An error occurred: {e}")


def tokenize_text(texts, text_tokenizer, max_length=128):
    """
    A function that returns tokens using BERT Tokenizer
    """
    tokens = text_tokenizer(
        texts.tolist(),
        padding=True,
        truncation=True,
        max_length=max_length,
        return_tensors="tf",
    )
    return tokens

# Define a function to split dataset
def split_dataset(dataset, split_ratio=0.1):
    """
    A funciton that splits dataset to return training and validation sets
    """
    # Shuffle dataset
    dataset = dataset.shuffle(buffer_size=1000)

    # Determine the number of examples
    num_examples = sum(1 for _ in dataset)
    num_train_examples = int(num_examples * (1 - split_ratio))

    # Split dataset
    train_dataset = dataset.take(num_train_examples)
    val_dataset = dataset.skip(num_train_examples)

    return train_dataset, val_dataset


# Get current working directory
cur_working_dir = os.getcwd()

# Get the relative data path of the input file directory
# REL_DATA_PATH   = '..\\data\\raw'
# REL_AFTER_PATH = '..\\data\\processed'

REL_DATA_PATH = "../data/raw"
REL_AFTER_PATH = "../data/processed"
# Join current working directory and relative data path to get the absolute
# to run dynamically on any system.
abs_data_path = os.path.join(cur_working_dir, REL_DATA_PATH)
abs_after_path = os.path.join(cur_working_dir, REL_AFTER_PATH)

FILE_FOR_PROCESSING = "leads_dataset.csv"
FILE_PROCESSED = "cleaned_leads.csv"

# Create input and output file paths
input_path = os.path.join(abs_data_path, FILE_FOR_PROCESSING)
output_path = os.path.join(abs_after_path, FILE_PROCESSED)


def get_datasets():
    """ method contains logic to return training and validation datasets"""
    # df= pd.read_csv('data/processed/cleaned_leads.csv', header = 0)
    df = pd.read_csv(output_path, header=0)
    df["text"] = (
        df["processed job_title"].astype(str)
        + " [SEP] "
        + df["processed Industry_name"].astype(str)
    )

    tokens = tokenize_text(df["text"], tokenizer)
    input_ids = tokens["input_ids"]
    attention_mask = tokens["attention_mask"]
    labels = df["lead_label"].values

    dataset = tf.data.Dataset.from_tensor_slices(
        ({"input_ids": input_ids, "attention_mask": attention_mask}, labels)
    )

    train_dataset, val_dataset = split_dataset(dataset, split_ratio=0.2)

    batch_size = 16
    train_dataset = train_dataset.shuffle(100).batch(batch_size)
    val_dataset = val_dataset.batch(batch_size)

    return train_dataset, val_dataset


if __name__ == "__main__":
    preprocess_data(input_path, output_path)

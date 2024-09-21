import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import os
from transformers import BertTokenizer, TFBertForSequenceClassification, AdamWeightDecay
from data_preprocessing import get_datasets  # Import the datasets

import tensorflow as tf

# Suppress most messages:
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)


def train_and_save_model():
    # Load datasets from data_preprocessing.py
    train_dataset, val_dataset = get_datasets()

    # Load pre-trained BERT tokenizer and model
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = TFBertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=3)  # 3 labels: cold, warm, hot

    # Fine-tuning
    optimizer = AdamWeightDecay(learning_rate=1e-5, weight_decay_rate=0.01)
    loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)

    model.compile(optimizer=optimizer, loss=loss_fn, metrics=['accuracy'])

    history = model.fit(
        train_dataset,
        validation_data=val_dataset,
        epochs=10  # Adjust the number of epochs as needed
    )

    loss, accuracy = model.evaluate(val_dataset)
    print(f'Validation Loss: {loss}')
    print(f'Validation Accuracy: {accuracy}')

    # Save the model and tokenizer
    model.save_pretrained('fine_tuned_bert')
    tokenizer.save_pretrained('fine_tuned_bert')

    # Create metrics directory if it does not exist
    metrics_dir = os.getenv('METRICS_DIR', 'metrics')  # Use environment variable or default to 'metrics'
    os.makedirs(metrics_dir, exist_ok=True)

    # Extract history data
    history_dict = history.history
    epochs = range(1, len(history_dict['loss']) + 1)

    # Plot training & validation loss values
    plt.figure(figsize=(12, 6))
    plt.plot(epochs, history_dict['loss'], 'bo-', label='Training Loss')
    plt.plot(epochs, history_dict['val_loss'], 'ro-', label='Validation Loss')
    plt.title('Training and Validation Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(metrics_dir, 'loss_plot.png'))
    plt.close()

    # Plot training & validation accuracy values
    plt.figure(figsize=(12, 6))
    plt.plot(epochs, history_dict['accuracy'], 'bo-', label='Training Accuracy')
    plt.plot(epochs, history_dict['val_accuracy'], 'ro-', label='Validation Accuracy')
    plt.title('Training and Validation Accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(metrics_dir, 'accuracy_plot.png'))
    plt.close()

    # Plot loss and accuracy on dual y-axes
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Plot loss
    color = 'tab:blue'
    ax1.set_xlabel('Epochs')
    ax1.set_ylabel('Loss', color=color)
    ax1.plot(epochs, history_dict['loss'], 'bo-', label='Training Loss')
    ax1.plot(epochs, history_dict['val_loss'], 'ro-', label='Validation Loss')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.legend(loc='upper left')

    # Create a second y-axis for accuracy
    ax2 = ax1.twinx()
    color = 'tab:green'
    ax2.set_ylabel('Accuracy', color=color)
    ax2.plot(epochs, history_dict['accuracy'], 'b--', label='Training Accuracy')
    ax2.plot(epochs, history_dict['val_accuracy'], 'r--', label='Validation Accuracy')
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.legend(loc='upper right')

    # Title and grid
    plt.title('Training and Validation Loss & Accuracy')
    fig.tight_layout()
    plt.grid(True)
    plt.savefig(os.path.join(metrics_dir, 'loss_accuracy_plot.png'))
    plt.close()

def load_model_and_tokenizer():
    # Load the model and tokenizer from the saved directory
    model = TFBertForSequenceClassification.from_pretrained('fine_tuned_bert')
    tokenizer = BertTokenizer.from_pretrained('fine_tuned_bert')
    return model, tokenizer

def predict_lead(job_title, industry):
    model, tokenizer = load_model_and_tokenizer()

    # Concatenate job title and industry
    text = f"{job_title} {industry}"
    tokens = tokenizer(text, padding=True, truncation=True, max_length=128, return_tensors='tf')
    outputs = model(**tokens)
    logits = outputs.logits.numpy()
    predicted_class = np.argmax(logits, axis=1)[0]
    labels = {0: 'cold', 1: 'warm', 2: 'hot'}
    
    return labels[predicted_class]

# Example usage for training
if __name__ == "__main__":
    train_and_save_model() 
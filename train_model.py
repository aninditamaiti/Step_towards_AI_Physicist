# -*- coding: utf-8 -*-
"""Train_Model_AI_Physicist.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1WfVSYN3mQzwklWj2OrHf0D3vXBjtMsB3
"""

!pip install transformers datasets beautifulsoup4 lxml requests

import os
import re
import html
import requests
from bs4 import BeautifulSoup
from datasets import Dataset

# List of source URLs (you can expand this list)
urls = [
    "https://arxiv.org/html/2506.14609v1"
]

!pip install -U transformers --quiet

from html_to_tex_converter import HTMLToLaTeXConverter

# Gather all texts
data_samples = []
urls = ["https://arxiv.org/html/2506.14609v1"]
for url in urls:
    try:
        text = HTMLToLaTeXConverter(url).extract_text_latex()
        if text.strip():
            data_samples.append({"text": text})
    except Exception as e:
        print(f"Error at {url}: {e}")

dataset = Dataset.from_list(data_samples)

# Tokenization and Transformer Fine-Tuning
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, DataCollatorForLanguageModeling

model_checkpoint = "distilgpt2"  # Small Transformer

tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
tokenizer.pad_token = tokenizer.eos_token  # avoid pad_token issues

# Tokenize the dataset
def tokenize_function(example):
    return tokenizer(example["text"], truncation=True, padding="max_length", max_length=512)

tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=["text"])

# Data collator
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

# Load model
model = AutoModelForCausalLM.from_pretrained(model_checkpoint)

"""I ran into a code version error for the train block, and edited as needed just to keep the code running within a time limit I had."""

from transformers import TrainingArguments, Trainer

training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=2,
    logging_steps=5,
    push_to_hub=False,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    tokenizer=tokenizer,
    data_collator=data_collator,
)

trainer.train()

"""# Training was bad
In the following chat-style conversion, I learned that the model has learned nothing about the actual research paper. This might be an issue with the data embedding, or an issue of the model. I need to debug that.
"""

# Chat-style Generation
from transformers import pipeline

text_generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

prompt = "Can you summarize the main idea of the paper in simple terms?"
response = text_generator(prompt, max_length=150, do_sample=True, temperature=0.7)
print("\nGenerated Chat-style Response:\n")
print(response[0]["generated_text"])
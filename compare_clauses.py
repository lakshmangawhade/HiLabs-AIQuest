from transformers import BertTokenizer, BertModel
import torch
import numpy as np

# It's recommended to handle model loading in a way that it doesn't happen on every call
# For simplicity in this script, we load it globally.
model_name = 'bert-base-uncased'
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertModel.from_pretrained(model_name)

def get_embedding(text, max_length=512):
    """Generate a sentence embedding for a given text using a BERT model."""
    # Clean and normalize text
    text = text.strip().lower()
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=max_length)
    with torch.no_grad():
        outputs = model(**inputs)
    # Use the mean of the last hidden state as the sentence embedding
    return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

def cosine_similarity(vec1, vec2):
    """Calculate the cosine similarity between two vectors."""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def classify_clause(extracted_clause, standard_clause, similarity_threshold=0.90):
    """Compare an extracted clause with a standard clause and classify it."""
    # If no clause was extracted from the contract, it's Non-Standard
    if not extracted_clause:
        return "Non-Standard"
    
    # If the standard clause is empty for some reason, we can't compare
    if not standard_clause:
        return "Non-Standard" # Or another category like 'No Standard Available'

    # 1. Exact Match Check (after normalization)
    if extracted_clause.strip().lower() == standard_clause.strip().lower():
        return "Standard"

    # 2. Semantic Similarity Check
    try:
        embedding1 = get_embedding(extracted_clause)
        embedding2 = get_embedding(standard_clause)
        
        similarity = cosine_similarity(embedding1, embedding2)
        
        # The threshold might need tuning based on observed results
        if similarity >= similarity_threshold:
            return "Standard"
        else:
            return "Non-Standard"
            
    except Exception as e:
        print(f"Error during semantic comparison: {e}. Falling back to basic check.")
        # Fallback to a simple substring check if the model fails
        if standard_clause.strip().lower() in extracted_clause.strip().lower():
            return "Standard"
        return "Non-Standard"

if __name__ == '__main__':
    # Example usage with the actual standard text
    standard_medicaid_filing = "Unless otherwise instructed, or required by Regulatory Requirements, Provider shall submit Claims to using appropriate and current Coded Service Identifier(s), within one hundred twenty (120) days from the date the Health Services are rendered or may refuse payment. If is the secondary payor, the one hundred twenty (120) day period will not begin until Provider receives notification of primary payor's responsibility."
    
    # Example 1: A slightly rephrased but semantically similar clause
    extracted_1 = "Provider must submit all claims within 120 days of service, unless we are the secondary payor."
    result_1 = classify_clause(extracted_1, standard_medicaid_filing)
    print(f"Comparison 1 -> {result_1}")

    # Example 2: A clause with a different time limit (clearly Non-Standard)
    extracted_2 = "Provider has 90 days to submit claims."
    result_2 = classify_clause(extracted_2, standard_medicaid_filing)
    print(f"Comparison 2 -> {result_2}")

    # Example 3: No clause found
    extracted_3 = ""
    result_3 = classify_clause(extracted_3, standard_medicaid_filing)
    print(f"Comparison 3 (empty) -> {result_3}")

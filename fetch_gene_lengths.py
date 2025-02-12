import pandas as pd
import requests
from Bio import Entrez
import time

# Set your email for NCBI
Entrez.email = "your_email@example.com"  # Replace with your email

def fetch_gene_info(gene_symbol):
    """
    Fetch gene information including mRNA length for a given gene symbol.
    """
    try:
        # Search for gene ID
        handle = Entrez.esearch(db="gene", term=f"{gene_symbol}[Gene Symbol] AND human[Organism]")
        record = Entrez.read(handle)
        handle.close()
        
        if not record['IdList']:
            return None
            
        gene_id = record['IdList'][0]
        
        # Fetch gene details
        handle = Entrez.efetch(db="gene", id=gene_id, retmode="xml")
        gene_record = Entrez.read(handle)
        handle.close()
        
        if not gene_record:
            return None
            
        gene_data = gene_record[0]
        
        # Get RefSeq transcript information
        handle = Entrez.elink(dbfrom="gene", db="nuccore", id=gene_id, linkname="gene_nuccore_refseqrna")
        link_record = Entrez.read(handle)
        handle.close()
        
        mrna_length = None
        if link_record[0]["LinkSetDb"]:
            mrna_id = link_record[0]["LinkSetDb"][0]["Link"][0]["Id"]
            handle = Entrez.efetch(db="nuccore", id=mrna_id, rettype="gb", retmode="xml")
            mrna_record = Entrez.read(handle)
            handle.close()
            
            if mrna_record:
                mrna_length = mrna_record[0]["GBSeq_length"]
        
        return {
            'gene_symbol': gene_symbol,
            'gene_id': gene_id,
            'mrna_length': mrna_length,
            'description': gene_data.get('Entrezgene_desc', ''),
            'chromosome': gene_data.get('Entrezgene_chromosome', '')
        }
        
    except Exception as e:
        print(f"Error fetching data for {gene_symbol}: {str(e)}")
        return None

def create_gene_database(gene_list):
    """
    Create a database for a list of gene symbols.
    """
    gene_data = []
    
    for gene in gene_list:
        print(f"Fetching data for {gene}...")
        data = fetch_gene_info(gene)
        if data:
            gene_data.append(data)
        time.sleep(1)  # Respect NCBI's rate limits
    
    # Create DataFrame
    df = pd.DataFrame(gene_data)
    
    # Save to CSV
    df.to_csv('gene_database.csv', index=False)
    print("Database saved to gene_database.csv")
    
    return df

# Example usage
example_genes = pd.read_csv('gene_names.csv')['gene'].tolist()

# Create database
gene_db = create_gene_database(example_genes)

# Display first few entries
print("\nFirst few entries in the database:")
print(gene_db.head())

# print(len(example_genes))
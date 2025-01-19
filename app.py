import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# App title
st.title("Internal Linking Opportunities Finder")

# File uploader for the keyword sheet
uploaded_file = st.file_uploader("Upload your Excel file with keywords and URLs", type=["xlsx"])

if uploaded_file:
    # Load the Excel file into a DataFrame
    list_keywords = pd.read_excel(uploaded_file)
    
    # Validate necessary columns
    required_columns = ["Keyword", "Position", "Search Volume", "Keyword Difficulty", "Page URL"]
    if all(col in list_keywords.columns for col in required_columns):
        st.success("File loaded successfully!")
        
        # Convert DataFrame to list of lists
        list_keywords = list_keywords.values.tolist()

        # Extract unique URLs
        list_urls = list(dict.fromkeys([x[4] for x in list_keywords]))

        # Keyword-URL-position pairs
        list_keyword_url = [[x[4], x[0], x[1]] for x in list_keywords]

        # Absolute route input
        absolute_rute = st.text_input("Insert your absolute route (e.g., https://example.com)")

        # Button to process the data
        if st.button("Find Internal Linking Opportunities"):
            if absolute_rute:
                internal_linking_opportunities = []

                # Iterate over URLs
                for iteration in list_urls:
                    try:
                        page = requests.get(iteration)
                        soup = BeautifulSoup(page.text, 'html.parser')

                        # Extract paragraphs and links
                        paragraphs = [p.text for p in soup.find_all('p')]
                        links = [link.get('href') for link in soup.find_all('a')]

                        # Check for linking opportunities
                        for x in list_keyword_url:
                            for y in paragraphs:
                                if f" {x[1].lower()} " in f" {y.lower()} ":
                                    if iteration != x[0]:
                                        links_presence = any(
                                            x[0].replace(absolute_rute, "") == z.replace(absolute_rute, "")
                                            for z in links if z
                                        )
                                        internal_linking_opportunities.append(
                                            [x[1], y, iteration, x[0], str(links_presence), x[2]]
                                        )
                    except Exception as e:
                        st.error(f"Error processing {iteration}: {e}")

                # Export results to Excel
                if internal_linking_opportunities:
                    output_df = pd.DataFrame(internal_linking_opportunities, columns=[
                        "Keyword", "Text", "Source URL", "Target URL", "Link Presence", "Keyword Position"
                    ])
                    output_file = "internal_linking_opportunities.xlsx"
                    output_df.to_excel(output_file, index=False)

                    st.success("Internal linking opportunities identified!")
                    with open(output_file, "rb") as f:
                        st.download_button(
                            label="Download Output File",
                            data=f,
                            file_name=output_file,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
            else:
                st.warning("Please enter an absolute route!")
    else:
        st.error("Uploaded file does not have the required columns!")

# Sidebar for app instructions
st.sidebar.title("How to Use This App")
st.sidebar.markdown("""
This tool helps content teams calculate the compression ratio of pages in order assess the quality and relevance of their content. The compression ratio gives insights into the following:

- **Risk of a future algorithmic penalty**
- **Absence of page identity**
- **Potential for ranking instabilities**
- **Redundancy of words, context, semantics, and entity relationships on the page**

### What is a Compression Ratio?
The compression ratio is the degree to which a page can be compressed without losing its identity or meaning. A higher compression ratio suggests that the content on the page is redundant, filled with filler words, and potentially low in quality. In contrast, a lower ratio suggests that the page is rich in content.

### Relevance in Content Marketing & SEO:
Search engines aim to save resources by compressing web content during indexing. Pages with high compression ratios (above 4.0) are considered to be spammy or full of fillers. This can hurt your rankings, cause traffic declines, and increase the risk of algorithmic penalties.

For better content marketing and SEO, focus on creating content that adds value and reduces redundancy, ensuring a low compression ratio.

[Read More Here](https://gofishdigital.com/blog/identify-low-quality-pages-compression-python-seo/)  )
""")

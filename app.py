import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Function to find internal linking opportunities
def find_internal_linking_opportunities(list_keywords, absolute_route):
    list_urls = []
    list_keyword_url = []
    internal_linking_opportunities = []

    # Extract unique URLs
    for x in list_keywords:
        list_urls.append(x[4])  # URL is at index 4 (5th column)
    list_urls = list(dict.fromkeys(list_urls))  # Remove duplicates

    # Extract URL and keyword information
    for x in list_keywords:
        list_keyword_url.append([x[4], x[0], x[1]])

    # Iterate over each unique URL
    for iteration in list_urls:
        page = requests.get(iteration)
        soup = BeautifulSoup(page.text, 'html.parser')
        paragraphs = soup.find_all('p')
        paragraphs = [x.text for x in paragraphs]

        links = []
        for link in soup.findAll('a'):
            links.append(link.get('href'))

        # For each keyword-URL pair in list_keyword_url
        for x in list_keyword_url:
            for y in paragraphs:
                if " " + str(x[1]).lower() + " " in " " + y.lower().replace(",", "").replace(".", "").replace(";", "").replace("?", "").replace("!", "") + " ":
                    if iteration != x[0]:
                        links_presence = False
                        for z in links:
                            try:
                                if x[0].replace(absolute_route, "") == z.replace(absolute_route, ""):
                                    links_presence = True
                            except AttributeError:
                                pass

                        if not links_presence:
                            internal_linking_opportunities.append([x[1], y, iteration, x[0], "False", x[2]])
                        else:
                            internal_linking_opportunities.append([x[1], y, iteration, x[0], "True", x[2]])

    return internal_linking_opportunities


# Streamlit UI
st.title("Internal Linking Finder")

st.write("""
Upload a spreadsheet containing keywords and their URLs, and provide the absolute route (base URL) for your website.
The app will analyze the content of the webpages and suggest internal linking opportunities.
""")

# File uploader for the user to upload their spreadsheet
uploaded_file = st.file_uploader("Choose a spreadsheet file", type=["xlsx"])

# Input for the absolute route
absolute_route = st.text_input("Enter the absolute route (base URL) of your website:")

if uploaded_file is not None and absolute_route:
    # Load the uploaded spreadsheet
    list_keywords = pd.read_excel(uploaded_file)

    # Convert the DataFrame into a list of lists
    list_keywords = list_keywords.values.tolist()

    # Call the internal linking function
    internal_linking_opportunities = find_internal_linking_opportunities(list_keywords, absolute_route)

    # Display the result in a dataframe
    if internal_linking_opportunities:
        st.write("Internal Linking Opportunities:")
        df = pd.DataFrame(internal_linking_opportunities, columns=["Keyword", "Text", "Source URL", "Target URL", "Link Presence", "Keyword Position"])
        st.dataframe(df)

        # Downloadable Excel option
        excel_file = df.to_excel(index=False)
        st.download_button(label="Download Result as Excel", data=excel_file, file_name="internal_linking_opportunities.xlsx", mime="application/vnd.ms-excel")
    else:
        st.write("No internal linking opportunities found.")
else:
    st.write("Please upload a file and enter the absolute route to begin.")

import streamlit as st
from streamlit_keplergl import keplergl_static
from keplergl import KeplerGl
import pandas as pd
import os
import altair as alt
import json

# Load the JSON configuration from file
file_path = 'kepler.gl.json'
with open(file_path, 'r') as file:
    config_data = json.load(file)
    
# Set default Streamlit page layout to wide mode
st.set_page_config(layout="wide")

indicator_descriptions  = {
    'Average Value of Savings Deposits in Banks': {
        'definition': 'This refers to the average amount of money individuals deposit in savings accounts within banks. Higher values may indicate greater disposable income or a propensity to save, reflecting a stable or growing economy.',
        'insight': 'Indicates the financial health and saving habits of residents, reflecting economic stability or growth potential.'
    },
    'Cluster Strength': {
        'definition': 'Refers to the concentration and strength of specific industries or economic clusters within a city, such as technology, manufacturing, or finance. A strong cluster suggests a thriving industry.',
        'insight': 'Reflects the specialization and competitive advantage of the city in particular industries, highlighting areas of economic growth and investment potential.'
    },
    'Number of ATMs Operating in the City': {
        'definition': 'Signifies the accessibility and penetration of banking services. Higher numbers could indicate a financially active population or increased urbanization.',
        'insight': 'Reflects the level of financial inclusion and convenience for residents, indicating the city\'s economic activity and development.'
    },
    'Number of Bank Branches Operating in the City': {
        'definition': 'Indicates the reach and accessibility of formal banking services within a city. More branches might suggest a robust financial infrastructure.',
        'insight': 'Reflects the city financial infrastructure and potential for economic growth, as more branches usually indicate higher accessibility to financial services.'
    },
    'Number of Incubation Centres & Skill Development Centres': {
        'definition': 'Represents the infrastructure and investment in nurturing entrepreneurship and skill development, fostering innovation and employability.',
        'insight': 'Indicates the city focus on fostering talent and innovation, leading to potential economic growth through a skilled workforce and entrepreneurial ventures.'
    },
    'Total Amount of Credit Disbursed by Banks among the Population of the City': {
        'definition': 'Reflects the availability and utilization of credit within the population, indicating consumer spending habits and investment activities.',
        'insight': 'Provides insights into the population purchasing power, investment appetite, and potential economic expansion through increased borrowing and spending.'
    },
    'Total Number of MSME Clusters in the City': {
        'definition': 'Represents the presence and strength of Micro, Small & Medium Enterprises (MSMEs) within the city, which are crucial for economic growth and employment generation.',
        'insight': 'Indicates the entrepreneurial activity, employment opportunities, and overall economic vibrancy within the city through the presence and growth of small and medium businesses. '
    },
    
}

def main():
    st.title("Insights on Economic Trends in Indian Cities")
    st.subheader("DeCODE (Deciphering City Outcomes through Data Exploration) Challenge")
    
    st.sidebar.title("Select the Economy Indicator")
    
    folder_path = "Data" # Replace this with your folder path
    files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

    selected_files = [st.sidebar.checkbox(file[:-4], value=False, key=file[:-4]) for file in files]

    map_1 = KeplerGl(height=600)
    
    selected_indicators = []
    
    
    for idx, file in enumerate(files):
        if selected_files[idx]:
            selected_indicators.append(file)
            file_path = os.path.join(folder_path, file)
            data = pd.read_csv(file_path)
            indicator_name = file[:-4]  # Modify this to match indicator names
            map_1.add_data(data=data, name=file)

             # Ensure the 'name' parameter matches the 'dataId' in the JSON config
            #data_name = config_data.get('config', {}).get('visState', {}).get('layers', [])[0].get('config', {}).get('dataId')
      
    map_1.config = config_data

    keplergl_static(map_1, center_map=True)    
    
    # Display highest and lowest city for selected indicators
    for indicator in selected_indicators:
      indicator_name = indicator[:-4]  # Removing the ".csv" extension
      st.write("Summary") 
      st.write(f"Indicator: {indicator_name}") 
      data = pd.read_csv(os.path.join(folder_path, indicator))
      unique_values = data['UOM'].unique()
      unique_text = ', '.join(unique_values)
      non_zero_values = data[data['Result'] != 0]  # Filter out zero values
      min_value = non_zero_values['Result'].min() if not non_zero_values.empty else data['Result'].max()
      highest_city = data[data['Result'] == data['Result'].max()]
      lowest_city = data[(data['Result'] == min_value)]
      avg_value = data['Result'].mean()

      
      if not highest_city.empty:
          st.write(f"Highest City: {highest_city['City'].values[0]}, Value: {highest_city['Result'].values[0]} {unique_text}")
      else:
          st.write("No data available.")


      if not lowest_city.empty:
          st.write(f"Lowest City: {lowest_city['City'].values[0]}, Value: {lowest_city['Result'].values[0]} {unique_text}")
      else:
          st.write("No data available.")
          
      st.write(f"Average Value for {indicator_name}: {avg_value:.2f} {unique_text}")

    charts = []

    for file in selected_indicators:
        data = pd.read_csv(os.path.join(folder_path, file))
        file_name = file[:-4]
        data = data[data['Result'].notnull()]

        if not data.empty:
            chart = alt.Chart(data).mark_circle().encode(
                x='City',
                y='Result:Q',
                color=alt.Color('Result:Q', scale=alt.Scale(scheme='viridis'), bin=alt.Bin(maxbins=6))
            ).properties(
                width=600,
                height=400,
                title=file_name
            ).interactive()

            charts.append(chart)
            
    if charts:
        #st.write("Charts for Selected Indicators:")
        for chart in charts:
            st.altair_chart(chart, use_container_width=True)
    else:
        st.write("Select the Economy Indicator")
    
    for selected_indicator in selected_indicators:
        # Remove the year portion from the selected indicator
        selected_indicator_no_year = selected_indicator.split('(')[0].strip()

        # Check if the modified selected indicator exists in the descriptions
        if selected_indicator_no_year in indicator_descriptions:
            #st.write(f"Indicator: {selected_indicator}")
            st.write(f"{indicator_descriptions[selected_indicator_no_year]['definition']}")
            st.write(f"{indicator_descriptions[selected_indicator_no_year]['insight']}")
        else:
            st.write(f"No description available for the selected indicator: {selected_indicator}")

    
if __name__ == "__main__":
    main()

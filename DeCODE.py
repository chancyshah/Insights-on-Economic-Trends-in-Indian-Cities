import streamlit as st
from streamlit_keplergl import keplergl_static
from keplergl import KeplerGl
import pandas as pd
import os
import altair as alt
import json

# Load the JSON configuration from file
file_path = 'D:/DeCODE/kepler.gl.json'
with open(file_path, 'r') as file:
    config_data = json.load(file)
    
    
# Set default Streamlit page layout to wide mode
st.set_page_config(layout="wide")

def main():
    st.title("Insights on Economic Trends in Indian Cities")
    st.subheader("DeCODE (Deciphering City Outcomes through Data Exploration) Challenge")
    
    st.sidebar.title("Select the Economy Indicator")
    
    folder_path = "D:/DeCODE/Data" # Replace this with your folder path
    files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

    selected_files = [st.sidebar.checkbox(file[:-4], value=False, key=file[:-4]) for file in files]

    map_1 = KeplerGl(height=600)
    
    selected_indicators = []
    
    data_id_mapping = {
        "Total Number of MSME Clusters in the City (2020-21)": "cukf9i4t",
        "Total Number of MSME Clusters in the City (2019-20)": "el67wa6f5" ,
        "Total Amount of Credit Disbursed by Banks among the Population of the City (2020-21)" : "7mywiax7f",
    }
    
    for idx, file in enumerate(files):
        if selected_files[idx]:
            selected_indicators.append(file)
            file_path = os.path.join(folder_path, file)
            data = pd.read_csv(file_path)
            indicator_name = file[:-4]  # Modify this to match indicator names
            data_id = data_id_mapping.get(indicator_name)
            if data_id:
                # If a dataId is found for the indicator, add the data with that dataId
                map_1.add_data(data=data, name=data_id)

            # Ensure the 'name' parameter matches the 'dataId' in the JSON config
            #data_name = config_data.get('config', {}).get('visState', {}).get('layers', [])[0].get('config', {}).get('dataId')
            #map_1.add_data(data=data, name=data_name)
    map_1.config = config_data

    keplergl_static(map_1, center_map=True)    
    
    # Display highest and lowest city for selected indicators
    for indicator in selected_indicators:
      indicator_name = indicator[:-4]  # Removing the ".csv" extension
      st.write(f"Indicator: {indicator_name}")
      data = pd.read_csv(os.path.join(folder_path, indicator))
      non_zero_values = data[data['Result'] != 0]  # Filter out zero values
      min_value = non_zero_values['Result'].min() if not non_zero_values.empty else data['Result'].max()
      highest_city = data[data['Result'] == data['Result'].max()]
      lowest_city = data[(data['Result'] == min_value)]
      avg_value = data['Result'].mean()

      
      if not highest_city.empty:
          st.write(f"Highest City: {highest_city['City'].values[0]}, Value: {highest_city['Result'].values[0]}")
      else:
          st.write("No data available.")


      if not lowest_city.empty:
          st.write(f"Lowest City: {lowest_city['City'].values[0]}, Value: {lowest_city['Result'].values[0]}")
      else:
          st.write("No data available.")
          
      st.write(f"Average Value for {indicator_name}: {avg_value:.2f}")

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
        st.write("Charts for selected indicators:")
        for chart in charts:
            st.altair_chart(chart, use_container_width=True)
    else:
        st.write("No data available for selected indicators.")
    
if __name__ == "__main__":
    main()

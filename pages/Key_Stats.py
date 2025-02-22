import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Key Stats",
    page_icon="👋",
)

st.title('Key Stats')
st.subheader('Useful statistics about each gender')

st.sidebar.header("Key Stats")
st.sidebar.subheader("Some Accuracy and Coverage statistics for each gender")
st.sidebar.text('Clicking on a barplot will display endings associated with its gender in the table below.')
st.sidebar.text('By learning ~30 endings (and 17 exceptions), you can pretty much learn the genders of more than half of all ~75k German nouns, and get them right 90% of the time!')
st.sidebar.text('Also, by learning only 8 endings (plus a couple of exceptions), you will cover 83% of all Female German nouns at over 90% accuracy. Wie zoll ist das?')
st.sidebar.text('For all the auditors out there, the total on this page doesn\'t agree to the DerDieDashboard because of the exclusion of exceptions. \nHave a medal 🥇')

def plot_stats(key_stats):
    key_stats = key_stats.rename({'coverage':'Coverage (%) of all nouns', 
                                  'accuracy':'Accuracy (%) of ending for gender'}, 
                                  axis = 0)
    pl = px.bar(key_stats.loc[['Accuracy (%) of ending for gender', 'Coverage (%) of all nouns']].round(2), 
       barmode = 'group',
       text = 'value',
       color_discrete_map={'n': 'green',
                                    'f': 'red',
                                    'm': 'blue',
                                    'total':'grey'},
       title = 'Accuracy and Coverage of Endings by Gender')

    # This fixes the text values to percentage format.
    pl.update_traces(textposition="outside",
                    texttemplate="%{y:.0%}")

    # This fixes the y-axis tickmarks to percentage format.
    pl.update_layout(yaxis_tickformat = '.0%',
                    yaxis_range=[0,1],
                    yaxis_title = None, xaxis_title = None, legend=dict(
                    yanchor="top",
                    y=1,
                    xanchor="right",
                    x=0.85),legend_title_text='Gender')
    
    return pl

def set_display_text(gender, num_end, word_count):
    st.session_state.stats['gender'] = gender
    st.session_state.stats['num_end'] = num_end
    st.session_state.stats['word_count'] = word_count

def filter_table():
    try:
        if st.session_state.end_filter['gender'] == 'total':
            table = st.session_state.key_endings.sort_values(by = 'total_endings', ascending = False).rename({'total_endings':'word_count'}, axis = 1)
            
            # Set values of dict used in subheader:
            #set_display_text('All',len(table),f'{table['word_count'].sum().astype(int):,}')
            return table
        else:
            table = st.session_state.key_endings.query(f'gender in {[st.session_state.end_filter['gender']]}').sort_values(by = 'total_endings', ascending = False).rename({'total_endings':'word_count'}, axis = 1)
            #set_display_text(st.session_state.end_filter['gender'],len(table), f'{table['word_count'].sum().astype(int):,}')
            
            return table
    except TypeError:
        table =  st.session_state.key_endings.sort_values(by = 'total_endings', ascending = False).rename({'total_endings':'word_count'}, axis = 1)
        #set_display_text('All',len(table),f'{table['word_count'].sum().astype(int):,}')
        return table

def extract_ending():
    try:
        gender = st.session_state.end_selected['selection']['points'][0]['legendgroup']
        aspect = st.session_state.end_selected['selection']['points'][0]['label']
        st.session_state.end_filter = {'gender':gender,
                                       'aspect':aspect}
        set_display_text(gender,
                         f'{st.session_state.key_stats.loc['num_endings'][gender].astype(int):,}', 
                         f'{st.session_state.key_stats.loc['total_endings'][gender].astype(int):,}')
    except IndexError:
        st.session_state.gender_selected = ''
        set_display_text('',
                         0, 
                         0)

if 'end_filter' not in st.session_state:
    st.session_state.end_filter = ''
if 'stats' not in st.session_state:
    st.session_state.stats = {'gender':'','num_end':0,'word_count':0}


st.plotly_chart(plot_stats(st.session_state.key_stats), key = 'end_selected', on_select=extract_ending)
if st.session_state.stats['gender'] == '':
    st.subheader('Nothing selected, displaying total:')
else:
    st.subheader(f'Selected: {st.session_state.stats['gender']}, with {st.session_state.stats['num_end']} endings, covering {st.session_state.stats['word_count']} words:')
st.dataframe(filter_table(), hide_index=True)

# This is the last problem to resolve:
# The issue is that this is out of sync. Instead of calculating values using the filter_table method, rather use the separate table used for graphing and just filter it for required values using dictionary.

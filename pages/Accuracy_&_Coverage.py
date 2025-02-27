import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Accuracy & Coverage",
    page_icon="👋",
)

st.subheader('Accuracy & Coverage by Gender')

st.sidebar.header("Identify the most important endings")
st.sidebar.text('Clicking on one of the barplots above will display accuracy & coverage of each ending for the selected gender.')
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
                                    'total':'indigo'},
                                    height = 300)

    # This fixes the text values to percentage format.
    pl.update_traces(textposition="inside",
                    texttemplate="%{y:.0%}")

    # This fixes the y-axis tickmarks to percentage format.
    pl.update_layout(yaxis_tickformat = '.0%',
                    yaxis_range=[0,1],
                    yaxis_title = None, xaxis_title = None, legend=dict(
                    yanchor="top",
                    y=1,
                    xanchor="right",
                    x=0.85),legend_title_text='Gender',
                    margin_b = 50,
                    margin_t = 20,
                    xaxis = dict(tickfont = dict(size=14)))
    
    return pl

def plot_acc_cov(accov, gender):
    if gender == 'total':
        return px.bar(title='Plot has been left intentionally blank, twice.')
    if gender == '':
        gender = 'f'
    # keep colouring consistent
    apply_colour = {'f':'red', 'm':'blue','n':'green'}
    colour_applied = apply_colour[gender]

    df = st.session_state.key_endings[['ending', 'gender','accuracy','coverage']].query(f'[\'{gender}\'] in gender').sort_values(accov, ascending = False)

    fig = px.bar(df, 
           x = 'ending', 
           y = accov,
           color = 'gender',
           color_discrete_sequence = [colour_applied],
           height = 300)
    
    fig.update_layout(showlegend = False, 
                      xaxis=dict(title=dict(text=str.title(accov+': '+gender))),
                      yaxis=dict(title=dict(text=str.title(''))),
                      margin_t = 10,
                      margin_l = 0,
                      margin_r = 20)
    fig.layout.yaxis.tickformat = ',.0%'
    
    return fig

def set_display_text(gender, num_end, word_count):
    st.session_state.stats['gender'] = gender
    st.session_state.stats['num_end'] = num_end
    st.session_state.stats['word_count'] = word_count

# This is not used, but still nice to keep.
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

try:
    st.plotly_chart(plot_stats(st.session_state.key_stats), key = 'end_selected', on_select=extract_ending)
    #if st.session_state.stats['gender'] == '':
    #    st.subheader('')
    #else:
        #st.write(f'Selected: {st.session_state.stats['gender']}, with {st.session_state.stats['num_end']} endings, covering {st.session_state.stats['word_count']} words:')

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plot_acc_cov('accuracy',st.session_state.stats['gender']), key = 'acc_plot')
    with col2:
        st.plotly_chart(plot_acc_cov('coverage',st.session_state.stats['gender']), key = 'cov_plot')
except AttributeError:
    st.subheader('Dashboard initialization error - please navigate to the \'DerDieDashboard\' page, and then back here, and the error will magically disappear 🧙')

# This is the last problem to resolve:
# The issue is that this is out of sync. Instead of calculating values using the filter_table method, rather use the separate table used for graphing and just filter it for required values using dictionary.

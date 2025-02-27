import streamlit as st
import pandas as pd
import plotly.express as px
from itertools import compress

st.set_page_config(
    page_title="DerDieDasboard",
    page_icon="👋",
)

words_melted = 'data/wf_melt.pkl'
ending_summary = 'data/end_summary.pkl'
key_endings = 'data/key_endings_v2.pkl'
key_stats = 'data/key_stats.pkl'

st.sidebar.subheader("The German gender demystifier you didn't know you needed")
st.sidebar.text('Finally, a way to more precisely visualize the relationships between German noun endings, and their genders. With this tool, you can easily learn the genders of over 55% of all 75k German nouns, at 90% accuracy!')
st.sidebar.text('Click on a barplot to explore the words and exceptions associated with each ending.')
st.sidebar.text('The little number above each plot indicates the accuracy of that ending (i.e. % of words belonging to that ending\'s majority gender.)')
st.sidebar.text('The tables below the plots present lists of words belonging to each gender.')
leipzig_url = 'https://wortschatz.uni-leipzig.de/en/download/German#deu_news_2024'

st.sidebar.text("\'usage\' is an indication of how common a word is, and was derived from several of [Leipzig University\'s corpora]")#% leipzig_url)


@st.cache_data #This prevents it from rerunning unless changes take place.
def read_files(file):
    df = pd.read_pickle(file)
    return df

# Pass two lists of endings and exceptions. Result = endings as keys, exceptions as values grouped with each applicable key.
def end_dict(my_endings, exceptions):
  
    end_except = {}

    for ending in my_endings:
        end_len = len(ending)
        except_list = []
        for exception in exceptions:
            except_len = len(exception)
            if end_len <= except_len and exception[-end_len:] == ending: # Length comparison prevents referencing exception.
                except_list.append(exception)
            end_except.update({ending:except_list})

    return end_except

# Reads endings from a separate table (summarised) for efficiency.
def count_endings():
    try:
        filtered = st.session_state.end_summary.query(f'ending in \'{st.session_state.my_table_filter}\'').iloc[0]
        for key in st.session_state.count_dict:
            st.session_state.count_dict[key] = filtered[key].item()
        
    except IndexError:
        for key in st.session_state.count_dict:
            st.session_state.count_dict[key] = 0

# Extract the selected point
def extract_selected():
    try:
        st.session_state.my_selected = st.session_state.my_end_sel['selection']['points'][0]['x']
        st.session_state.my_table_filter = st.session_state.my_end_sel['selection']['points'][0]['x']
        count_endings()
        st.session_state.my_selected_exceptions = st.session_state.end_except_dict[str(st.session_state.my_selected)]
    except IndexError:
        st.session_state.my_selected = ''
        st.session_state.my_table_filter = ''
        st.session_state.my_selected_exceptions = []
        count_endings()
    except  KeyError:
        st.session_state.my_selected_exceptions = ''
        count_endings()

def extract_exceptions():
    try:
        st.session_state.my_table_filter = st.session_state.my_except_sel['selection']['points'][0]['x']
        count_endings()
    except IndexError:
        st.session_state.my_table_filter = ''
        count_endings()

def melted_plot(endings, heading, leg_vis, plot_width):
    # Find endings in table that are in endings selected by user.
    quer = f'ending in {endings}'
            
    end_pivot = st.session_state.wf_melt.query(quer).pivot_table(index = 'ending',
                                        columns = 'Gender',
                                        values = 'Word',
                                        aggfunc = 'count',
                                        fill_value = 0).reset_index()
    end_pivot['total'] = end_pivot[end_pivot.columns[1:]].sum(axis = 1)
    end_pivot['accuracy'] = round(end_pivot.drop(['ending','total'], axis = 1).max(axis = 'columns')/end_pivot['total']*100,0)
    end_pivot = end_pivot.sort_values('total', ascending = False)
    total_words = sum(end_pivot['total'])

    barchart = px.bar(end_pivot.sort_values('total', ascending=False).drop('total', axis = 1).head(21),
                x='ending', 
                y=list(compress(['f','m','n'],[x in end_pivot.columns for x in ['f','m','n']])), # Prevents crash when < 3 genders
                title=f'{heading} {total_words:,} words',
                text = list(end_pivot['accuracy']),
                color_discrete_map={'n': 'green',
                                    'f': ' red',
                                    'm': 'blue'},
                width = plot_width)

    # This fixes a stupid problem whereby accuracy labels are repeated. Therefore only showing labels for gender n.
    barchart.update_traces(textposition="outside", cliponaxis=False)
    barchart.for_each_trace(
        lambda trace: trace.update(text="") if trace.name != "n" else (),
    )

    barchart.update_layout(yaxis_title = None, xaxis_title = None, legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="right",
                    x=0.99),legend_title_text='Gender',
                    margin=dict(t=50, b=50), height = 350,
                    activeselection=dict(opacity=0))
    
    # Hide legend for exceptions plot
    if leg_vis == 0:
        barchart.update_layout(showlegend = False)

    return barchart

def pivot_table(gender,ending):
    pt = st.session_state.wf_melt.query(f'ending in \'{ending}\' and Gender == \'{gender}\'').drop(['Gender', 'ending'], 
                                                                                                   axis = 1).rename({'count':'usage'}, axis = 1)
    return pt
                                                                                                             

# Creating the session state variables

# Reading the files to be used:
if "wf_melt" not in st.session_state:
    st.session_state.wf_melt = read_files(words_melted)
if "end_summary" not in st.session_state:
    st.session_state.end_summary = read_files(ending_summary)
if "key_stats" not in st.session_state:
    st.session_state.key_stats = read_files(key_stats)
if "key_endings" not in st.session_state:
    st.session_state.key_endings = read_files(key_endings)

if 'end_except_dict' not in st.session_state:
    st.session_state.end_except_dict = {"e":["yte","bote","see"],"ng":["ang","ing"],"iel":[],"in":["ein"],"er":["tier","pier"],"mus":[],"haus":[],"it":[],"ft":["äft"],"hen":[],"f":["hiff"],"um":["aum"],"rm":["orm"],"em":[],"ik":[],"uch":["buch","tuch"],"tz":["etz"],"ei":["hrei","brei"],"all":[],"eis":['leis'],"ld":['ald','uld']}

if 'my_table_filter' not in st.session_state:
    st.session_state.my_table_filter = ''    
if 'my_selected_exceptions' not in st.session_state:
    st.session_state.my_selected_exceptions = []
if 'my_selected' not in st.session_state:
    st.session_state.my_selected = []
if 'count_dict' not in st.session_state:
    st.session_state.count_dict = {'m':0,'f':0,'n':0, 'total':0,'m_perc':0.0,'f_perc':0.0,'n_perc':0.0}

# Title & subtitle.
st.title('DerDieDashboard')
st.write('A data visualization project by Michael Urson - Enjoy!')

# Create graphs, one for endings, another for exceptions.
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(melted_plot(list(st.session_state.end_except_dict.keys()), f'Endings: ',1, 300), key = 'my_end_sel',on_select = extract_selected)
with col2:
    st.plotly_chart(melted_plot(st.session_state.my_selected_exceptions,'Exceptions: ',0,50), key = 'my_except_sel', on_select = extract_exceptions)

# Display which item is selected and number of occurrences.
if st.session_state.my_table_filter == '':
    st.subheader('Nothing selected.')
else:
    st.subheader(f'Selected: [{st.session_state.my_table_filter}] {st.session_state.count_dict['total']:,}')

# Create tables for each gender.
col3, col4, col5 = st.columns(3)
with col3:
    st.write(f":red[Feminine: {st.session_state.count_dict['f']:,} ({st.session_state.count_dict['f_perc']:.0%})]")
    st.dataframe(pivot_table('f',st.session_state.my_table_filter), hide_index=True, height = 200, width = 200)
with col4:
    st.write(f":blue[Masculine: {st.session_state.count_dict['m']:,} ({st.session_state.count_dict['m_perc']:.0%})]")
    st.dataframe(pivot_table('m',st.session_state.my_table_filter), hide_index=True, height = 200, width = 200)
with col5:
    st.write(f":green[Neutral: {st.session_state.count_dict['n']:,} ({st.session_state.count_dict['n_perc']:.0%})]")
    st.dataframe(pivot_table('n',st.session_state.my_table_filter), hide_index=True, height = 200, width = 200)
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 22:44:49 2023

@author: Stephen
"""

import streamlit as st
import pandas as pd
import json 
import os,re


# Load data
@st.experimental_singleton
def load_data():
    f = open('abstract-Representa-set.txt',encoding='utf8')
    inData = ''.join(f.readlines()); f.close()
    entries = inData.split('\n\n\n'); data={}
    for idx, entry in enumerate(entries):
        lines = entry.split('\n\n')
        auths = lines[2].replace('\n',' ').replace('(','$^').replace(')','$ ').strip('.')
        for i, line in enumerate(lines):
            if 'DOI: ' in line:
                info = lines[i]
        data[idx] = {
            'citation' : lines[0].replace('\n',' ').replace(':','\:').split(' ',1)[-1],
            'title'    : lines[1].replace('\n',' '), 
            'authors'  : auths,
            'abstract' : lines[4].replace('\n',' '), 
            'info'     : info}
    print('Read pubmed')
    return data

# Add notes to current state
def add_to_state(notesDict):
    for k in notesDict:
        if k.endswith('_note'):
            st.session_state[k] = notesDict[k]
    st.session_state['working'] = notesDict['working']
    print('Added notes to state')

def updateNote(k):
    name = st.session_state['name']
    note = st.session_state[f'{k}_tmp']
    
    st.session_state[f'{k}_note']['Name'].append(name)
    st.session_state[f'{k}_note']['Note'].append(note)
    st.session_state[f'{k}_tmp'] = ""
    print_data()
    print('Updated Note')

def load_notes(clicked=False):
    if os.path.isfile('notes.json'):
        with open('notes.json','r') as f:
            notesDict = json.load(f)
    else:
        notesDict = {'working':False}
    print('Read in notes')
    if clicked:
        add_to_state(notesDict)
        print_data()
    return notesDict

def get_notes(clicked=False):
    copy = st.session_state.to_dict()
    tmp = {}
    tmp['working'] = copy['working']
    for k in copy:
        if k.endswith('_note'):
            tmp[k] = copy[k]
    if clicked:
        print_data()
    print ('Got notes')
    return tmp

def saveNotes():
    tmp = get_notes()
    if len(tmp) > 1:
        with open('notes.json','w') as f:
            json.dump(tmp,f)
    print_data()
    print('Saved notes')
    return

def popLastNote(k):
    if len(st.session_state[f'{k}_note']['Note']) > 0:
        st.session_state[f'{k}_note']['Name'].pop()
        st.session_state[f'{k}_note']['Note'].pop()
    print_data()
    return

def toggleWork():
    st.session_state['working'] = not bool(st.session_state['working'])
    print_data()
    return

# Only run once
data       = load_data()
notesDict  = load_notes()
paperRange = (1,10)
  
if 'working' not in st.session_state:
    add_to_state(notesDict)    

# Write out the main text
def print_data():
    st.write('\n## Papers\n---')
    for k in range(paperRange[0]-1,paperRange[1]-1):
        if f'{k}_note' not in st.session_state:
            st.session_state[f'{k}_note'] = {'Name':[],'Note':[]}
        st.write(
f''':red[*Paper {k+1}* | {data[k]['citation']}] \n### {data[k]['title']}
#### {data[k]['authors']}
{data[k]['abstract']}\n\n''',
    '**Notes**: ')
        st.table(st.session_state[f'{k}_note'])
        st.text_area('New Note:', key=f'{k}_tmp',on_change=updateNote,
                           args=(k,))
        st.button('Remove last entry',key=f'{k}_pop',on_click=popLastNote, args=(k,))
        st.write('\n\n-----\n\n')    

# Begin Writing!
sidebar = '''
# Welcome :wave:

This is a way to make it easier to perform pubmed reviews (hopefully). This demo
here was generated by typing the following pubmed search querie:
    
> "Represenational Similarity Analysis" AND "fMRI" 

To download all the notes, click here!
'''
st.sidebar.write(sidebar)
st.sidebar.write('###### Please enter your name so that notes can be saved with your name')
st.sidebar.text_input('Name',key='name',on_change=print_data)
st.sidebar.button('Load Notes',key='load',on_click=load_notes,kwargs={'clicked':True})
st.sidebar.button('Save Notes',on_click=saveNotes)
st.sidebar.download_button('Download notes', data=str(get_notes()), file_name='notes.json',on_click=print_data)
st.sidebar.write('''# :orange[Note] 
The currrent application has the risk of notes being over written if multiple
people are working on the document at the same time. To avoide this, please 
toggle the below button when you are working on adding notes :smile:''')
st.sidebar.button('Is someone working?',key='_button',on_click=toggleWork)
st.sidebar.write('# ' + str(st.session_state['working']))
st.sidebar.write('''---\n# Responsive \n To keep the webpage responsive, select which 
articles you would like to be diplayed''')
paperRange = st.sidebar.slider('slide',1,len(data)+1,(1,10))
st.sidebar.button('Apply!',key='apply_change',on_click=print_data)







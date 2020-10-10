# Importing libraries
import base64
import datetime
import io

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import dash_table

from Sales_Commentary_Generation_Helper import *

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Creating app
app.layout = html.Div([
    html.H1("J&J: Financial Commentary Generation Tool", style = {'textAlign': 'center', 'color': '#D71500'}),
	html.Div(children = "Automate L1/L2 commentary generation by simply plugging in the sales file and setting up a few parameters!", style={
        'textAlign': 'center'}),
	html.Hr(),  # horizontal line
	
	html.H3("Input Fields:",style = {'color': '#D71500'}),
	dcc.Markdown(children = "1. Please upload the sales file in wide format:"),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select File')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=False
    ),
	html.Div(id='output-data-upload'),
	html.Br(),
	
	dcc.Markdown("2. Please enter the all the geographical columns in the dataset separated by commas (i.e. - Country, MRC, Cluster, Region):"),
	
	html.Div([
    dcc.Input(id='Region_columns' , type='text'),
	html.Button(id='region_submit', n_clicks=0, children='Submit Geographical columns'),
	
	
	html.Br(),
	html.Br(),
	
	dcc.Markdown("3. Hierarchy Check"),
	dcc.Markdown("*Please ensure that both the overall hierarchy and geographical hierarchy are correct. Since this app is not fixed to any particular hierarchy of any business unit, getting the product hierarchy correct is absolutely necessary.*"),
	html.Label(id='The automated hierarchies identified are:'),
	html.Div(id='hierarchy_statement'),
              #dcc.Input(id='overall_hierarchy_input' , type='text')]),
	#html.Div(id='regional_hierarchy_output'),
              #dcc.Input(id='regional_hierarchy_input', type='text')]),
	
	]),
	html.Hr(),		  
	#html.Button(id='proceed', n_clicks=0, children='Proceed', style={'color': 'green'}),
	
	#html.Button(id='Change_hierarchy', n_clicks=0, children='Incorrect Hierarchy Detected! Click here to change!',style={'color': 'red'}),
	html.Div([ html.Div(children = '*3a: Please ignore this section if the hierarchy is correctly identified',style={'color': 'red'}),
		html.Div([html.Label("Enter new overall hierarchy in descending order: (Geographical + Product Hierarchy) (comma separated)"),
              dcc.Input(id='new_overall_hierarchy_input', value = 'Country, FranchiseLevel1, FranchiseLevel2, SKU', type='text')]),
		html.Br(),
		html.Div([html.Label("Enter new geographical hierarchy here: (comma separated)"),
              dcc.Input(id='new_regional_hierarchy_input', value = 'Country', type='text')]),
			  
		html.Button(id='new_hierarchy_submit', n_clicks=0, children='Submit New Hierarchy')
		]),
	html.Div(id='new_hierarchy_submission'),
	
	################################################################
	html.Hr(),
	html.H3("Provide conditions for which commentary should be generated:",style = {'color': '#D71500'}),
	html.Label('Month:', style = {'font-weight': 'bold'}),
    dcc.Dropdown(
		id = 'Month_Selection',
        options=[
		    {'label': 'All months', 'value': 'All'},
			{'label': 'January', 'value': 'Jan'},
            {'label': 'February', 'value': 'Feb'},
            {'label': 'March', 'value': 'Mar'},
            {'label': 'April', 'value': 'Apr'},
			{'label': 'May', 'value': 'May'},
            {'label': 'June', 'value': 'Jun'},
            {'label': 'July', 'value': 'Jul'},
			{'label': 'August', 'value': 'Aug'},
            {'label': 'September', 'value': 'Sep'},
            {'label': 'October', 'value': 'Oct'},
			{'label': 'November', 'value': 'Nov'},
            {'label': 'December', 'value': 'Dec'},
        ],
        placeholder = "Select a month or select all",
		clearable=False,
		searchable = False
    ),
	html.Br(),
	html.Div([
    html.Label('Comparison Plan:', style = {'font-weight': 'bold'}),
    dcc.RadioItems(
		id = 'Comparison_Plan',
        options=[
            {'label': 'All Plans', 'value': 'All'},
            {'label': 'Previous Year (PY)', 'value': 'PY'},
            {'label': 'Full Business Plan (FBP)', 'value': 'FBP'},
			{'label': 'June Update (JU)', 'value': 'JU'},
			{'label': 'November Update (NU)', 'value': 'NU'},
        ],
        value='All'
    ),
	
    html.Label('Period:', style = {'font-weight': 'bold'}),
    dcc.RadioItems(
		id = 'Period_Selection',
        options=[
            {'label': 'All Periods', 'value': 'All'},
            {'label': 'YTD', 'value': 'YTD'},
            {'label': 'QTD', 'value': 'QTD'},
			{'label': 'MTD', 'value': 'MTD'}
        ],
        value='All'
    ),
	html.Label('Variance from baseline above which commentary will be generated (Million USD):', style = {'font-weight': 'bold'}),
    dcc.Input(id = 'h_1_value',value=0.5, type='number', min = 0),
	
	html.Label('%Variance from baseline above which commentary will be generated (percentage change):', style = {'font-weight': 'bold'}),
    dcc.Input(id = 'h_1_perc', value=15, type='number', max = 100, min = 0),
	
	html.Label('Threshold for products of lower hierarchy to be included in commentary (Million USD):', style = {'font-weight': 'bold'}),
    dcc.Input(id = 'h_2_value',value=0.1, type='number', min = 0),
	
	html.Label('%Threshold for products of lower hierarchy to be included in commentary (percentage change):', style = {'font-weight': 'bold'}),
    dcc.Input(id = 'h_2_perc',value=15, type='number', max = 100, min = 0),
	], 
	
	style={'columnCount': 2}),
	html.Br(),
	html.Label('Hierarchy at which commentary should be generated (please select a column from within the hierarchy columns):', style = {'font-weight': 'bold'}),
    dcc.Input(id = 'commentary_hierarchy',value='FranchiseLevel2', type='text'),
	html.Br(),
	html.Button(id='conditions_submit', n_clicks=0, children='Submit all input details!', style = {'horizontalAlign': 'middle'}),
	html.Div(id='commentary_generation', style={'color': 'blue'}),
	dcc.Markdown('This step might take some time depending on your choices. Please refer to the console window for completion status'),
	
	
	# Hidden div inside the app that stores the intermediate value
    html.Div(id='original_df', style={'display': 'none'}),
	html.Div(id='new_overall_hierarchy_hidden', style={'display': 'none'}),
	
])


def read_file(contents, filename):
	content_type, content_string = contents.split(',')
	decoded = base64.b64decode(content_string)
	try:
		if 'csv' in filename:
            # Assume that the user uploaded a CSV file
			df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
			return df
		elif 'xls' in filename:
			# Assume that the user uploaded an excel file
			df = pd.read_excel(io.BytesIO(decoded))
			return df
	except Exception as e:
		print(e)
		return html.Div([
            'There was an error processing this file.'
        ])
	
@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename')]
			  )
def update_output(list_of_contents, list_of_names):
	if list_of_contents is not None:
		df = read_file(list_of_contents, list_of_names)
		
		return html.Div([
        html.H5(list_of_names),
		#html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            data=df[:50].to_dict('records'), # Show only top 50 rows
            columns=[{'name': i, 'id': i} for i in df.columns],
			virtualization=True,
			page_size = 10,
			fixed_rows={'headers': True},
			style_header={
			'fontWeight': 'bold'
			},
        )
	]	
    )

@app.callback(Output('original_df', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename')]
			  )
def storing_table(list_of_contents, list_of_names):
	if list_of_contents is not None:
		df = read_file(list_of_contents, list_of_names)
		return df.to_json(date_format='iso', orient='split')
	
region_hierarchy = []
overall_hierarchy = []

@app.callback(Output('hierarchy_statement', 'children'),
				[Input('region_submit','n_clicks')], 
				[State('original_df', 'children'), State('Region_columns','value')])
def hierarchy_confirm(n_clicks, data, Region_columns):
	if data is not None and Region_columns is not None:
		df = pd.read_json(data, orient='split')
		Region_columns = [x.strip() for x in Region_columns.split(',')]
		Region_columns_check = all(elem in df.columns for elem in Region_columns)
		if Region_columns_check:
			global region_hierarchy, overall_hierarchy
			region_hierarchy, overall_hierarchy = hierarchy_finder(df, Region_columns = Region_columns)
		#print(region_hierarchy, overall_hierarchy)
			return u'''The overall hierarchy detected from the data is: {} and the geographical hierarchy is: {}'''.format(overall_hierarchy, region_hierarchy)
		else:
			return u'''Geographical or NTS column(s) not found in data. Please check the column name and try again!'''
	else:
		return u'''Geographical columns not provided or data set not uploaded - this statement will update after completion of task 1 & 2.'''

'''
def new_hierarchy_finalise():
	global region_hierarchy, overall_hierarchy
	def subfunction(n_clicks, new_overall_hierarchy, new_regional_hierarchy):	
		global region_hierarchy, overall_hierarchy
		if (n_clicks == 0) |  (new_overall_hierarchy is None) | (new_regional_hierarchy is None):
			return None
		else:
			region_hierarchy = [new_regional_hierarchy]
			overall_hierarchy = [new_overall_hierarchy]
			html.Label("New overall hierarchy and regional hierarchy:", overall_hierarchy, region_hierarchy)
			return uHierarchies changed to {} & {}.format(region_hierarchy, overall_hierarchy) 
'''
'''
def subfunction(n_clicks, new_overall_hierarchy, new_regional_hierarchy):	
	global region_hierarchy, overall_hierarchy
	if (n_clicks == 0) |  (new_overall_hierarchy is None) | (new_regional_hierarchy is None):
		return None
	else:
		region_hierarchy = [new_regional_hierarchy]
		overall_hierarchy = [new_overall_hierarchy]
		html.Label("New overall hierarchy and regional hierarchy:", overall_hierarchy, region_hierarchy)
		return uHierarchies changed to {} & {}.format(region_hierarchy, overall_hierarchy) 
'''

@app.callback(Output('new_hierarchy_submission', 'children'),
				[Input('new_hierarchy_submit','n_clicks')], 
				[State('new_overall_hierarchy_input','value'),
				State('new_regional_hierarchy_input','value'), 
				State('original_df', 'children')]) 
def new_hierarchy(n_clicks, new_overall_hierarchy_input, new_regional_hierarchy_input, data):
	global region_hierarchy, overall_hierarchy
	if (n_clicks == 0) | (new_overall_hierarchy_input is None) | (new_regional_hierarchy_input is None):
		return None
	else:
		df = pd.read_json(data, orient='split')
		new_overall_hierarchy_input = [x.strip() for x in new_overall_hierarchy_input.split(',')]
		new_regional_hierarchy_input = [x.strip() for x in new_regional_hierarchy_input.split(',')]
		overall_check = all(elem in df.columns for elem in new_overall_hierarchy_input)
		regional_check = all(elem in df.columns for elem in new_regional_hierarchy_input)
		
		if (overall_check) & (regional_check):
			region_hierarchy = new_regional_hierarchy_input
			overall_hierarchy = new_overall_hierarchy_input
			return '''The hierarchies have been changed to: {} & {} respectively'''.format(overall_hierarchy, region_hierarchy)
		else:
			return '''Columns entered not found in data - please enter again!'''


@app.callback(Output('commentary_generation', 'children'),
				[Input('conditions_submit','n_clicks')], 
				[State('Month_Selection','value'),
				State('Comparison_Plan','value'), 
				State('Period_Selection','value'),
				State('h_1_value','value'),
				State('h_1_perc','value'),
				State('h_2_value','value'),
				State('h_2_perc','value'),
				State('commentary_hierarchy','value'),
				State('original_df', 'children')]) 	
def calculating_commentary(n_clicks, month, comparison, period, h_1_value, h_1_perc, h_2_value, h_2_perc, commentary_hierarchy, data):
	global lower_hierarchy_value_thresh, lower_hierarchy_perc_thresh
	#print(region_hierarchy, overall_hierarchy)
	if data is None:
		return None
	else:
		if commentary_hierarchy not in overall_hierarchy:
			return '''You have specified a hierarchy not part of the overall hierarchy provided! Please check the hierarchy column name given.'''
		df = pd.read_json(data, orient='split')
		lower_hierarchy_dict, commentaries_calculation = commentary_calculations(sales_df = df, 
																						commentary_hierarchy = commentary_hierarchy, 
																						Month = month, 
																						Plan = comparison, 
																						Period_type = period,
																						overall_hierarchy = overall_hierarchy,
																						region_hierarchy = region_hierarchy,
																						lower_hierarchy_value_thresh = h_2_value, 
																						lower_hierarchy_perc_thresh = h_2_perc)
		
		if (lower_hierarchy_dict is not None) & (commentaries_calculation is not None):
			print("Calculations complete! Moving to writing commentaries")
			commentary_df = commentary_necessary_data(commentaries_calculation, lower_hierarchy_dict, 
														numerical_value = h_1_value, percentage_value = h_1_perc)
			numerical_value = h_1_value
			percentage_value = h_1_perc
			commentary_list = []
			i = 0
			for index, row in commentary_df.iterrows():
				# split condition if commentary level hierarchy meets the desired threshold
				if (abs(row['h_1_value']) >= numerical_value) | (abs(row['h_1_percentage']) >= percentage_value):
					value = round(row['h_1_value'],2)
					value_str = '$' + str(value) + 'MM'
					
					if row['h_1_percentage'] !=0:
						percent = round(row['h_1_percentage'] ,1)
						value_str = value_str + '(' + str(percent) + '%)'
					
					# Main hierarchy comment
					subject = row[commentary_hierarchy]
					subject = subject.replace('&', 'and')
					subject = NP(subject)
					
					# Choosing verb
					if value > 0:
						verb = VP(random.choice(main_hierarchy_increase))
					else:
						verb = VP(random.choice(main_hierarchy_decrease))
						
					
					objekt = NP('vs.', row['Comparitive'], value_str)
					comment = Clause()
					comment.subject = subject
					comment.predicate = verb
					comment.object = objekt
					comment['TENSE'] = 'PAST'
					
					# Lower Hierarchy details
					samedirection_impact = []
					opposite_impact = []
					if len(lower_hierarchy_dict[index]) == 0:
						comment_realise = pd.Series(realise(comment))
					else: # when lower hierarchy details are present
						lowh_comment = Clause()
						
						if len(lower_hierarchy_dict[index]) <= 2:
							comment.complements += random.choice(subordinate_adverb) # words like mainly, primarily
						
						#language is split by sign of main hierarchy value
						for key, lowerhierarchy_value in sorted(lower_hierarchy_dict[index].items(), key = lambda item: -item[1][0]): #sorting by descending order $ impact!!
							key = key.replace('&','and')
							value_to_append = pd.Series(key + '(' + str(round(lowerhierarchy_value[0],2)) + 'MM)')
							if ((lowerhierarchy_value[0] > 0) & (row['h_1_value'] > 0)) | ((lowerhierarchy_value[0] < 0) & (row['h_1_value'] < 0)):
								samedirection_impact.append(value_to_append.values[0])
							else:
								opposite_impact.append(value_to_append.values[0])
						
						if len(samedirection_impact) > 0:
							if len(samedirection_impact) > 1: ## Purely Asthetic purpose
								samedirection_comment = ", ".join(samedirection_impact[:len(samedirection_impact) - 1]) + ' and ' + samedirection_impact[len(samedirection_impact)-1]
							else:
								samedirection_comment = ", ".join(samedirection_impact)
							lowh_comment.subject = samedirection_comment
							lowh_comment['COMPLEMENTISER'] = random.choice(subordinate_clause) ## adding words like due to, from etc.
							comment.complements += lowh_comment
						
						# Subordinate offset clause
						if len(opposite_impact) > 0:
							#print(opposite_impact)
							if len(opposite_impact) > 1:
								opposite_impact.reverse() #Reversing the list so order of magnitude of impact is highest to lowest
							opposite_comment = ", ".join(opposite_impact)
							negate_clause = Clause(opposite_comment)
							negate_clause['COMPLEMENTISER'] = random.choice(subordinate_clause_negate)
							#negate_clause['COMPLEMENTISER'] = random.choice(['but','although'])
							comment.complements += negate_clause        
						
						# Final comment
						comment_realise = pd.Series(realise(comment))
					commentary_list.append(comment_realise[0])
					#print(comment_realise[0])
					
				# commentary where upper threshold is < than set but lower hierarchies have significant movements
				else: #Marginal difference impacted by xxx
					subject = NP(random.choice(main_hierarchy_alternate))
					verb = VP(random.choice(main_hierarchy_alternate_verb))
					comment = Clause()
					comment.subject = subject
					comment.predicate = verb
					comment['TENSE'] = 'PAST'
					
					lower_hierarchy_list = []
					for key, lowerhierarchy_value in sorted(lower_hierarchy_dict[index].items(), key = lambda item: -item[1][0]):
						key = key.replace('&','and')
						value_to_append = pd.Series(key + '(' + str(round(lowerhierarchy_value[0],2)) + 'MM/' +  str(round(lowerhierarchy_value[1],2)) + '%)')
						lower_hierarchy_list.append(value_to_append.values[0])
					
					if len(lower_hierarchy_list) > 1:
						lower_hierarchy_object = ", ".join(lower_hierarchy_list[:len(lower_hierarchy_list) - 1]) + ' and ' + lower_hierarchy_list[len(lower_hierarchy_list)-1]
					else: 
						lower_hierarchy_object = ", ".join(lower_hierarchy_list)
					
					comment.object = NP('by',lower_hierarchy_object)
					comment_realise = pd.Series(realise(comment))
					commentary_list.append(comment_realise[0])
				
				#print(index)
				#print(comment_realise[0])
				i += 1
				if i%100 == 0:
					print(i, "rows complete!")    

			commentary_df['Commentary'] = commentary_list
			if len(commentary_df) == 0:
				return '''No commentary was writen as the thresholds were not exceeded! Please re-adjust the thresholds to generate commentaries if required'''
			else:
				commentary_df.to_csv("generated_commentary.csv", index = False)
				return '''Commentary Generated! Please refer to the file 'generated_commentary.csv' to view them'''
		
		else:
			return '''You are generating commentaries at a very low product group hierarchy. Please move up at-least 1 hierarchy!'''
			
if __name__ == '__main__':
    app.run_server(debug=True)
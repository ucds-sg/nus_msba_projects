####################################################################################################################################################################
# import resources
import pandas as pd
import numpy as np
import datetime as dt
import os # for navigating to the required directory
import itertools #for iterating through lists of data
import pickle
import random #picking random elements out of lists

## NLG libraries
from nlglib.realisation.simplenlg.realisation import Realiser
from nlglib.microplanning import *


realise = Realiser(host='nlg.kutlak.info')


# Log is a wrapper - it allows for functions inside functions
def log_dataframe(f):
    def wrapper(dataf, *args, **kwargs):
        tic = dt.datetime.now()
        result = f(dataf, *args, **kwargs)
        toc = dt.datetime.now()
        print(f"{f.__name__} took={toc - tic} shape = {result.shape}")
        return result
    return wrapper

def log(f):
    def wrapper(*args, **kwargs):
        tic = dt.datetime.now()
        result = f(*args, **kwargs)
        toc = dt.datetime.now()
        print(f"{f.__name__} took={toc - tic}")
        return result
    return wrapper

# Pointing our notebook to the data directory dynamically
path_parent = os.path.dirname(os.getcwd())
#os.chdir(path_parent + "\\Datasets")
# Confirm the directory
#print(os.getcwd())


####################################################################################################################################################################
# Defining all calculation functions

# Determining Hierarchy
@log
def hierarchy_finder(sales_data, Region_columns):
    r"""
    
    Given a conusmer sales file with certain "Region columns", certian "Product Hierarchy" columns and NTS data, finds the product hierarchy and geographic hierarchy
    
    Parameters
    ----------
    Data-Frame: Consumer Sales Data
    Region_columns = list or str of data specifying the columns which are of region type
    
    Returns
    -------
    product_hierarchy, region_hierarchy
        lists with products and regions sorted by hierarchy
    
    """
    #Removing NTS columns
    Columns_to_remove = sales_data.columns[sales_data.columns.str.match('NTS')]
    # Removing period column as well
    Columns_to_remove = Columns_to_remove.append(pd.Index(['Period']))
    Region_columns = sales_data[Region_columns].columns
    
    ## Hierarchy for products
    Columns_to_remove = Columns_to_remove.append(Region_columns)
    Filtered_data = sales_data.drop(columns = Columns_to_remove)
    print("Columns on which product hierarchy will be tested are:", Filtered_data.columns)
    
    # Figuring out the hierarchy
    hierarchy_columns = Filtered_data.columns
    product_hierarchy_list = []
    
    if len(hierarchy_columns) > 1:
        for combinations in itertools.permutations(hierarchy_columns, 2):
            print("Combination is: ", combinations)
            temp_h1 = combinations[0]
            temp_h2 = combinations[1]
            temp_data = Filtered_data.groupby(temp_h1)[temp_h2].nunique()
            #print(temp_data)
            if np.any(temp_data > 1):
                print(temp_h1, "is above", temp_h2, "in hierarchy." )
                product_hierarchy_list.append(combinations)
            else:
                print(temp_h1, "is NOT above", temp_h2, "in hierarchy." )
        
        product_hierarchy_dataframe = pd.DataFrame(product_hierarchy_list, columns = ['Upper_h','Lower_h'])
        product_hierarchy = list(product_hierarchy_dataframe.Upper_h.value_counts().index)
        product_hierarchy_lower = product_hierarchy_dataframe.Lower_h.value_counts().index[0]
        product_hierarchy.append(product_hierarchy_lower)
        print("Product hierarchy from the data is:", product_hierarchy)
    else:
        print("Only 1 column detected - that is the only hierarchy available")
        product_hierarchy = [hierarchy_columns.values[0]] 
    
    ## Hierarchy for Region
    #Columns_to_remove = Columns_to_remove.append(Region_columns)
    Filtered_data = sales_data[Region_columns]
    print("Columns on which regional hierarchy will be tested are:", Filtered_data.columns)
    
    # Figuring out the hierarchy
    hierarchy_columns = Filtered_data.columns
    region_hierarchy_list = []
    
    if len(hierarchy_columns) > 1:
        for combinations in itertools.permutations(hierarchy_columns, 2):
            print("Combination is: ", combinations)
            temp_h1 = combinations[0]
            temp_h2 = combinations[1]
            temp_data = Filtered_data.groupby(temp_h1)[temp_h2].nunique().sort()
            if np.any(temp_data > 1):
                print(temp_h1, "is above", temp_h2, "in hierarchy." )
                region_hierarchy_list.append(combinations)
            else:
                print(temp_h1, "is NOT above", temp_h2, "in hierarchy." )
        
        region_hierarchy_dataframe = pd.DataFrame(region_hierarchy_list, columns = ['Upper_h','Lower_h'])
        region_hierarchy = list(region_hierarchy_dataframe.Upper_h.value_counts().index)
        region_hierarchy_lower = region_hierarchy_dataframe.Lower_h.value_counts().index[0]
        region_hierarchy.append(region_hierarchy_lower)
        print("Region hierarchy from the data is:", product_hierarchy)
    else:
        print("Only 1 column detected - that is the only hierarchy available", hierarchy_columns.values)
        region_hierarchy = [hierarchy_columns.values[0]] 
    
    ## ASSUMPTION 1: REGIONAL HIERARCHY WILL ALWAYS BE ABOVE PRODUCT HIERARCHY
    ## i.e say a hierarchy of (country_cluster -> country -> region) will always precede (FL1 -> FL2 -> SKU)
    overall_hierarchy = region_hierarchy + product_hierarchy
    return region_hierarchy, overall_hierarchy

@log
def consumer_sales_data(sales_df, overall_hierarchy):
    r"""
    
    Manipulates Consumer data to long format
    
    Parameters
    ----------
    sales_df = Consumer sales Data in wide format
    
    Returns
    -------
    Dataframe = sales data in long format
    
    """
    print("Sales data is of the shape: ", sales_df.shape)

    # Removing spaces from column names to ensure long to wide conversion
    sales_df.columns = sales_df.columns.str.replace(' ','')
    wide_to_long_LHS_list = overall_hierarchy.copy()
    wide_to_long_LHS_list.append('Period')
    sales_concat_longformat = pd.wide_to_long(sales_df,stubnames='NTS', i = wide_to_long_LHS_list, 
                                              j = 'Comparision_period', suffix=r'\w+')
    sales_concat_longformat.reset_index(drop = False, inplace = True) 

    # Seperating month and comparision period columns
    sales_concat_longformat['Period Type'] = sales_concat_longformat['Comparision_period'].str[3:]
    sales_concat_longformat['Period Type'] = sales_concat_longformat['Period Type'].str.replace("", 'MTD')
    sales_concat_longformat['Period Type'] = sales_concat_longformat['Period Type'].str.replace('MTDQMTDTMTDDMTD', 'QTD')
    sales_concat_longformat['Period Type'] = sales_concat_longformat['Period Type'].str.replace('MTDYMTDTMTDDMTD', 'YTD')
    sales_concat_longformat['Month'] = sales_concat_longformat['Comparision_period'].str[:3]
    print("Sales table after converting it to long format is of dimensions: ", sales_concat_longformat.shape)

    # Getting correct comparitives
    sales_concat_longformat["Plan"] = sales_concat_longformat["Period"].str[:-5]
    sales_concat_longformat["Plan"] = sales_concat_longformat["Plan"].str.replace(" ","")

    #sales_concat_longformat["Plan"] = sales_concat_longformat["Plan"].str.replace

    sales_concat_longformat.drop(columns = ['Comparision_period'], inplace = True)
    return sales_concat_longformat

#final_sales_data = consumer_sales_data(sales_df = sales_2018)
#final_sales_data

## Next Step is to create a full fledged dataset at the level Period (YTD, QTD, MTD) - Comparision - Month - Year - Country - Product (The valid ones) and map it to Clean_dataset above to understand when commentaries are necessary and when they are not
@log
def create_fulldataset():
    r"""
    
    Creates a data-frame that gives all possible combinations of commentaries possible
    
    Parameters
    ----------
    None
    
    Returns
    -------
    Dataframe
    
    """
    Period_dict = {'Period Type': ['YTD', 'MTD', 'QTD'], 'Key': 1}
    df_period = pd.DataFrame(Period_dict)
    df = df_period.merge(pd.DataFrame({'Comparitive': ['FBP', 'JU', 'NU', 'PY'],'Key': 1}), how = 'outer') \
        .merge(pd.DataFrame({'Month_key':[1,2,3,4,5,6,7,8,9,10,11,12], 
                         'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul',
                                      'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                         ,'Key': 1}),how = 'outer' )
    
    # To prevent retrospective calculations (like JU available in January!!), these rows will be removed
    #df = df[~((df['Comparitive'] == 'JU') & (df['Month_key']<4))] #JU available from April (normally)
    #df = df[~((df['Comparitive'] == 'NU') & (df['Month_key']<9))] #NU available after mid-August (normally)
    
            #.merge(pd.DataFrame({'Country': ['China OTC', 'Vietnam', 'Taiwan', 'Hong Kong', 'Indonesia',
         #                                   'Japan', 'Korea', 'Thailand', 'Malaysia', 'China Skincare', 
          #                                  'Singapore', 'India', 'Philippines', 'APSC', 'China Skin', 
           #                                'Pacific'],'Key': 1}), how = 'outer') \
            
    return df

# function that filters and rolls up lower hierarchy datadata
def lower_hierarchy_calculations(index, conditions, hierarchy_dictionary, lower_hierarchy_value_thresh = 0.1, lower_hierarchy_perc_thresh = 14.5):
    r"""

    Filters, rolls up and calculates required data
    
    Parameters
    ----------
    index: index of for loop 
    conditions 
    sales_df_lower_hierarchy: sales data rolled-up to a hierarchy below the level at which commentary is required
    
    Returns
    -------
    lower_level_dict: dictionary with entity, value and percentage value! In v2, 3rd level hierarchy values can be added as dict entities as well
    #lists of entity, value and percentages of lower level hierarchy values
    
    period_type, month, hierarchy, regional_hierarchy,plan
    """
    # Dictionaries where data will be stored
    data = {}
    
    if len(conditions) == 4: # No region hierarchy in this data 
        period_type = conditions[0]
        month = conditions[1]
        hierarchy = conditions[2]
        plan = conditions[3]
    
        current_condition = (sales_data_rolledup_h2.Period_Type == period_type) & \
                                                       (sales_data_rolledup_h2.Month == month) & \
                                                       (sales_data_rolledup_h2[hierarchy_dictionary['h_1']] == hierarchy)
        
        filtered_data = sales_data_rolledup_h2[current_condition]
        
        for product in filtered_data[filtered_data['Plan'] == 'ACT'][hierarchy_dictionary['h_2']].unique(): #Loop over only the product-groups with actual sales this year
            comparative_value = filtered_data[(filtered_data.Plan == plan) & (filtered_data[hierarchy_dictionary['h_2']] == product)].NTS.values
            actual_value = filtered_data[(filtered_data.Plan == 'ACT') & (filtered_data[hierarchy_dictionary['h_2']] == product)].NTS.values
            
            if (comparative_value.size != 0) & (actual_value.size != 0):
                actual_value = actual_value[0]
                comparative_value = comparative_value[0]
                
                diff = (actual_value - comparative_value)/1000000
                perc = ((actual_value - comparative_value)/abs(comparative_value)) * 100

                if (abs(diff) >= lower_hierarchy_value_thresh)|(abs(perc) > lower_hierarchy_perc_thresh):

                    ## Storing these values in dictionary
                    data[product] = [diff, perc]
        
        return data
        
    if len(conditions) == 5: # With region hierarchy 
        period_type = conditions[0]
        month = conditions[1]
        hierarchy = conditions[2]
        regional_hierarchy = conditions[3]
        plan = conditions[4]
        
        current_condition = (sales_data_rolledup_h2.Period_Type == period_type) & \
                                                       (sales_data_rolledup_h2.Month == month) & \
                                                       (sales_data_rolledup_h2[region_hierarchy[-1]] == regional_hierarchy) & \
                                                       (sales_data_rolledup_h2[hierarchy_dictionary['h_1']] == hierarchy)
        
        filtered_data = sales_data_rolledup_h2[current_condition]
        
        
        for product in filtered_data[filtered_data['Plan'] == 'ACT'][hierarchy_dictionary['h_2']].unique(): #Loop over only the product-groups with actual sales this year
            comparative_value = filtered_data[(filtered_data.Plan == plan) & (filtered_data[hierarchy_dictionary['h_2']] == product)].NTS.values
            actual_value = filtered_data[(filtered_data.Plan == 'ACT') & (filtered_data[hierarchy_dictionary['h_2']] == product)].NTS.values
            
            if (comparative_value.size != 0) & (actual_value.size != 0):
                actual_value = actual_value[0]
                comparative_value = comparative_value[0]
                
                diff = (actual_value - comparative_value)/1000000
                perc = ((actual_value - comparative_value)/abs(comparative_value)) * 100

                if (abs(diff) >= lower_hierarchy_value_thresh)|(abs(perc) > lower_hierarchy_perc_thresh):
                    ## Storing these values in dictionary
                    data[product] = [diff, perc]
                    
        return data
        
# Creating a function that filters the full dataset according to required parameters and aggregates it to the required level of commentary

def commentary_calculations(sales_df, commentary_hierarchy, Month, Plan, Period_type, 
							overall_hierarchy, region_hierarchy, 
							lower_hierarchy_value_thresh, lower_hierarchy_perc_thresh):
    
    global sales_data_rolledup_h2 ##Making lower level hierarchy dataset global so that this dataset doen't need to be called everytime 'lower_hierarchy_calculations' is called
    r"""

    Filters the full dataset according to required parameters and brings it to the required level
    
    Parameters
    ----------
    commentary_hierarchy, Month, Plan, Period Type
    sales_df: sales data in the input format provided to Analytics team - wide format
    
    Returns:
    -------
    Dataframe
    
    """
    
    # Checking if 'commentary hierarchy entered is part of overall hierarchy'
    if commentary_hierarchy not in overall_hierarchy:
        print("You have specified a hierarchy not part of the overall hierarchy provided! Program will exit")
        return None
    
    # Importing conusmer data
    sales_data = consumer_sales_data(sales_df = sales_df, overall_hierarchy = overall_hierarchy)
    
    
    # Filtering for required conditions
    if(Month != 'All'):
        sales_data = sales_data[sales_data['Month'] == Month]
    
    if(Period_type != 'All'):
        sales_data = sales_data[sales_data['Period Type'] == Period_type]

    #if(Country != 'All'):
     #   sales_data = sales_data[sales_data['Country'] == Country]

    if(Plan != 'All'):
        sales_data = sales_data[(sales_data['Plan'] == Plan) | (sales_data['Plan'] == 'ACT')]
        if(Plan == 'ACT'):
            Plan_alternate == 'PY'
            print("Caution! You will be comparing against PY Actuals!")
    
    if sales_data.shape[0] == 0:
        print("One of the filters entered does not exist, please check the value of the filter!")
        return None
            
    # Position of required roll-up in hierarchy
    number_of_hierarchies = len(overall_hierarchy) - (overall_hierarchy.index(commentary_hierarchy)+1)
    print("There are",number_of_hierarchies, "product hierarchies below the level of commentary generation")
    
    # Dictionary storing the hierarchy values
    if number_of_hierarchies == 0:
        print("You are generating commentaries at a very low product group hierarchy. Please move up atleast 1 hierarchy")
        return None
    else:
        hierarchy_dict = {}
        i = 0
        ## WE WILL NOT GO BELOW 3 LEVELS OF HIERARCHY FOR ANY COMMENTARY
        while i<=number_of_hierarchies:
            key = 'h_' + str(i+1)  #h = hierarchy with 1 starting from the top
            value = overall_hierarchy[i-number_of_hierarchies-1]
            hierarchy_dict[key] = value
            i += 1
            if i == 3:
                break
        
        #Get an empty template
        df_empty = create_fulldataset()
        
        # Filtering empty template according to conditions
        if(Month != 'All'):
            df_empty = df_empty[df_empty['Month'] == Month]
    
        if(Period_type != 'All'):
            df_empty = df_empty[df_empty['Period Type'] == Period_type]

        #if(Country != 'All'):
         #   sales_data = sales_data[sales_data['Country'] == Country]

        if(Plan != 'All'):
            if Plan == 'ACT':
                df_empty = df_empty[df_empty['Comparitive'] == 'PY']
            else:
                df_empty = df_empty[df_empty['Comparitive'] == Plan]
        
        ## If df_empty(the template) has a filter that causes problems, return None (Mailny applied for 'Plan' filter which was causing problems)
        if df_empty.shape[0] == 0:
            print("One of the filters entered does not exist, please check the value of the filter!")
            return None
        
        ## Rolling up procedures
        Current_year = sales_data['Period'].str[-4:].unique().max()
        Current_year_actual = str('ACT ' + Current_year)
        Last_year = str(int(sales_data['Period'].str[-4:].unique().max()) - 1)
        Last_year_actual = str('ACT ' + Last_year) #For finding actual values of last year data
        
        # Template for commentaries
        df_hierarchy = sales_data[sales_data['Period'] == Current_year_actual]  # template only for products where actual data for current year is present
        df_hierarchy = df_hierarchy[overall_hierarchy[:overall_hierarchy.index(commentary_hierarchy)+1]] ## All columns with hierarchies above (and including required) are joined
        df_hierarchy.drop_duplicates(inplace = True)
        df_hierarchy['Key'] = 1
        all_commentaries_df = df_empty.merge(df_hierarchy, how = 'outer', on = 'Key') ## This join ensures the integrity of certain products in certain countries
        all_commentaries_df.columns = all_commentaries_df.columns.str.replace(' ','_')
        all_commentaries_df.drop(columns = ['Key'], inplace = True)
        print("Commentary template is of the shape:", all_commentaries_df.shape)
        #df_commentary_values = all_commentaries_df.copy()
        
        
        # Rolling up data
        ## Lower level hierarchy values - h2 hierarchy
        groupby_list_h2 = ['Period', 'Period Type', 'Month', 'Plan'] + overall_hierarchy[:overall_hierarchy.index(commentary_hierarchy)+2]
        sales_data_rolledup_h2 = sales_data.groupby(groupby_list_h2)[['NTS']].sum().reset_index(drop = False)
        print("Lower level hierarchy roll-up successful")
        sales_data_rolledup_h2['Plan'] = np.where(sales_data_rolledup_h2['Period'] == Last_year_actual, 'PY',sales_data_rolledup_h2['Plan'])
        sales_data_rolledup_h2.columns = sales_data_rolledup_h2.columns.str.replace(' ','_')

        ## Commentary level roll-up
        groupby_list = ['Period', 'Period_Type', 'Month', 'Plan'] + overall_hierarchy[:overall_hierarchy.index(commentary_hierarchy)+1]
        sales_data_rolledup = sales_data_rolledup_h2.groupby(groupby_list)[['NTS']].sum().reset_index(drop = False)
        print("Commentary level hierarchy roll-up successful")
        

        ## Getting required values of data
        out_v = [] #value output
        out_p = [] #percentage output
        remark = [] # remarks on comparitive
        lower_hierarchy_dict = {}
        if commentary_hierarchy not in region_hierarchy:
            for index, row in all_commentaries_df.iterrows():
                
                period_type = row.Period_Type
                month = row.Month
                regional_hierarchy = row[str(region_hierarchy[-1])]
                hierarchy = row[hierarchy_dict['h_1']]
                plan = row.Comparitive

                condition = (sales_data_rolledup.Period_Type == period_type) & \
                                                       (sales_data_rolledup.Month == month) & \
                                                       (sales_data_rolledup[region_hierarchy[-1]] == regional_hierarchy) & \
                                                       (sales_data_rolledup[hierarchy_dict['h_1']] == hierarchy) 

                filter_df = sales_data_rolledup[condition]

                comparative_value = filter_df[filter_df.Plan == plan].NTS.values
                actual_value = filter_df[filter_df.Plan == 'ACT'].NTS.values
                

                if ((comparative_value.size == 0) | (actual_value.size == 0)):
                    value = 0
                    percentage = 0
                    rem = pd.Series("Comparative value not found")
                else:
                    comparative_value = comparative_value[0]
                    actual_value = actual_value[0]
                    
                    ## Calling hierarchy level 2 function
                    lower_hierarchy_calc = lower_hierarchy_calculations(index = index, 
                                                         conditions = [period_type, month, hierarchy, regional_hierarchy,plan], 
                                                         hierarchy_dictionary = hierarchy_dict,
														 lower_hierarchy_value_thresh = lower_hierarchy_value_thresh, 
														 lower_hierarchy_perc_thresh = lower_hierarchy_perc_thresh)
                    lower_hierarchy_dict[index] = lower_hierarchy_calc
                    
                    
                    # Commentary level calculations
                    if comparative_value == 0:
                        percentage = 0
                        value = (actual_value-comparative_value)/1000000
                        rem = pd.Series("Comparitive value is 0 - Percentage calculation not possible")
                    elif (comparative_value<0) | (actual_value < 0):
                        percentage = ((actual_value-comparative_value)/abs(comparative_value)) * 100
                        value = (actual_value-comparative_value)/1000000
                        rem = pd.Series("Negative actual or planned values detected")
                    else:
                        percentage = ((actual_value-comparative_value)/abs(comparative_value)) * 100
                        value = (actual_value-comparative_value)/1000000
                        rem = pd.Series("None")
                
                if index%5000 == 0:
                    print(index)

                out_p.append(percentage)
                out_v.append(value)
                remark.append(rem.values[0])
        else:
            for index, row in all_commentaries_df.iterrows():
                period_type = row.Period_Type
                month = row.Month
                #regional_hierarchy = row[region_hierarchy[-1]]
                hierarchy = row[hierarchy_dict['h_1']]
                plan = row.Comparitive

                condition = (sales_data_rolledup.Period_Type == period_type) & \
                                                       (sales_data_rolledup.Month == month) & \
                                                       (sales_data_rolledup[hierarchy_dict['h_1']] == hierarchy) 

                filter_df = sales_data_rolledup[condition]

                comparative_value = filter_df[filter_df.Plan == plan].NTS.values
                actual_value = filter_df[filter_df.Plan == 'ACT'].NTS.values
                
                
                if ((comparative_value.size == 0) | (actual_value.size == 0)):
                    value = 0
                    percentage = 0
                    rem = pd.Series("Comparative value not found")
                else:
                    ## Calling hierarchy level 2 function
                    lower_hierarchy_calc = lower_hierarchy_calculations(index = index, 
                                                         conditions = [period_type, month, hierarchy,plan], 
                                                         hierarchy_dictionary = hierarchy_dict,
														 lower_hierarchy_value_thresh = lower_hierarchy_value_thresh, 
														 lower_hierarchy_perc_thresh = lower_hierarchy_perc_thresh)
                    lower_hierarchy_dict[index] = lower_hierarchy_calc
                    
                    
                    # Commentary level calculations
                    comparative_value = comparative_value[0]
                    actual_value = actual_value[0]
                    
                    if comparative_value == 0:
                        percentage = 0
                        value = (actual_value-comparative_value)/1000000
                        rem = pd.Series("Comparitive value is 0 - Calculation not possible")
                    elif (comparative_value<0) | (actual_value < 0):
                        percentage = ((actual_value-comparative_value)/abs(comparative_value)) * 100
                        value = (actual_value-comparative_value)/1000000
                        rem = pd.Series("Negative actual or planned values detected")
                    else:
                        percentage = ((actual_value-comparative_value)/abs(comparative_value)) * 100
                        value = (actual_value-comparative_value)/1000000
                        rem = pd.Series("None")
                if index%5000 == 0:
                    print(index)

                out_p.append(percentage)
                out_v.append(value)
                remark.append(rem.values[0])
        
        # Appending values to dataframe
        #out_p = pd.Series()
        all_commentaries_df['h_1_value'] = out_v #pd.Series(out_v).values
        all_commentaries_df['h_1_percentage'] = out_p
        all_commentaries_df['Remarks'] = remark
        return lower_hierarchy_dict, all_commentaries_df
        #print(all_commentaries_df)


def commentary_necessary_data(commentary_calculation_data, lowerhierarchy_dict, numerical_value, percentage_value):
    commentary_calculation_data = commentary_calculation_data[commentary_calculation_data['Remarks'] != 'Comparative value not found']
    # Filters based on level 1 hierarchy values
    commentary_calculation_data_filtered = commentary_calculation_data[(abs(commentary_calculation_data['h_1_value'] >= numerical_value)) | 
                                                              (abs(commentary_calculation_data['h_1_percentage'] >= percentage_value))]
   # Filters based on lower level hierarchy values - only filter for keys which have some elements
    filter_keys = []
    for key in lowerhierarchy_dict.keys():
        if len(lowerhierarchy_dict[key]) > 0:
            filter_keys.append(key)
    
    commentary_data = commentary_calculation_data[(commentary_calculation_data.index.isin(commentary_calculation_data_filtered.index)) | #upper hierarchy filter
                                                  (commentary_calculation_data.index.isin(filter_keys))] #lower hierarchy filter
    
    return commentary_data

### Vocabulary area
main_hierarchy_increase = ['increase', 'overperform', 'grow']
main_hierarchy_decrease = ['decrease', 'underperform', 'decline']

subordinate_clause = ['due to', 'from', 'driven by', 'owing to', 'on account of', 'thanks to']
subordinate_clause_negate = ['offset by']
subordinate_adverb = ['mainly', 'primarily', 'especially', 'majorly', 'largely']

main_hierarchy_alternate = ['Marginal difference','Actual in-line']
main_hierarchy_alternate_verb = ['impact','affect']
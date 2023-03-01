from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, CDSView, BooleanFilter
from bokeh.plotting import figure
from bokeh.models.widgets import Select

# create a data source
source = ColumnDataSource(data=dict(x=[1, 2, 3, 4, 5], y=[2, 5, 4, 6, 7]))

# create a filter
filter = BooleanFilter([True, True, True, True, True])

# create a CDSView using the filter and data source
view = CDSView(filter=filter)

# create a plot using the CDSView
plot = figure(title="Filtered Scatter Plot", tools="box_select,lasso_select")
plot.scatter('x', 'y', source=source, view=view, size=10)
print('0', filter.booleans)
# create a callback function to update the filter
def update_filter(attr, old, new):
    print('1',new, filter.booleans)
    if new == "":
        filter.booleans = [True] * len(source.data['x'])
        
    else:
        selected_indices = [True for i in range(int(new))]
        filter_array = [False for i in range(len(filter.booleans)-len(selected_indices))]
        selected_indices.extend(filter_array)
        #for i in selected_indices:
        #    filter_array[i] = True
        filter.booleans = selected_indices
        view.filter =  BooleanFilter(filter.booleans)
    print('2',new,filter.booleans)


# create a select widget
select = Select(title="Select indices to filter", value="", options=["", "0", "1", "2", "3", "4"])
select.on_change('value', update_filter)

# create a layout for the plot and select widget
layout = column(plot, select)

# add the layout to the current document
curdoc().add_root(layout)

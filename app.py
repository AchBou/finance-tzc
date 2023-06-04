from flask import Flask, render_template, request

from src.data_calculation import calculate_data
from src.data_scrapring import load_data
from src.graph_visualization import construct_graph_data

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        # Process data from the form
        date = request.form.get('data')
        yyyy, mm, dd = date.split('-')
        data = load_data(dd, mm, yyyy)
        if data:
            c_data = calculate_data(data[2])
            graph_data = construct_graph_data(c_data[1], c_data[4])
            return render_template('index.html', columns=data[0], data=data[1], date=date,
                                   maturity=c_data[0], tmp=c_data[2], ta=c_data[3], tzc=c_data[4],
                                   graph_data=graph_data)
    return render_template('index.html')


if __name__ == '__main__':
    app.run()

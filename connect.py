from flask import Flask, render_template, request
import image
import lr
import slr
import clr
import op
import lalr

app = Flask(__name__)
gram = 0
lip = []
option = 0
tables = 0


@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/table', methods=['GET', 'POST'])
def table():
    return render_template("table.html")


@app.route('/parser', methods=['GET', 'POST'])
def parse():
    if request.method == 'POST':
        global option
        option = request.form.get('par')
        print(option)
        if (option == "lr"):
            dic = lr.parse(lip, 0, "")
            print(dic["table"])
            file = open("C:\\Users\\himanshu\\PycharmProjects\\pythonProject\\table.txt", 'w')
            file.write(dic["table"])
            file.close()
        elif (option == "slr"):
            print(lip)
            file = open("C:\\Users\\himanshu\\PycharmProjects\\pythonProject\\grammar\\5.txt", 'w')
            for ele in lip:
                file.write(ele + '\n')
            file.close()
            slr.main([])
        elif option == "clr":
            global tables
            lip.append("")
            tables = clr.main(lip, 0, 0)
        elif option == "op":
            op.take(lip)
        elif option == "lalr":
            lalr.main(lip, "")

        return render_template('table.html')
    return render_template('parser.html', name=gram)


@app.route('/grammar', methods=['GET', 'POST'])
def contact():
    if (request.method == 'POST'):
        gram = request.form.get('name')
        li = list(gram.split("\n"))
        print(li)
        global lip
        lip = []
        ll = li[-1]
        for i in li:
            lip.append(i[:-1])
        del lip[-1]
        lip.append(ll)
        # print(lip)
        return render_template('parser.html', name=li)
    return render_template('grammar.html')


@app.route('/stringta', methods=['GET', 'POST'])
def connn():
    if (request.method == 'POST'):
        st = request.form.get('names')
        name = request.form.get('inputfile')
        ss = "images/" + name
        a = str(st)

        if a == "String":
            x = image.img(ss)
            a = ""
            for i in x:
                a = a + str(i)
            print(a)
        else:
            x = []
            x.append(a)

        if option == "lr":
            file = open("C:\\Users\\himanshu\\PycharmProjects\\pythonProject\\stack.txt", 'w')
            for a in x:
                dic = lr.parse(lip, 1, a)

                file.write(dic["stack"])
                file.write('\n')
            file.close()

        elif option == "slr":
            slr.main(x)
        elif option == "clr":
            clr.main(lip, a, tables)
        elif option == "op":
            op.main(a)
        elif option == "lalr":
            lalr.main(lip, a)
        return render_template('table_1.html')
    return render_template('stringta.html')


if __name__ == '__main__':
    app.run(debug=True)

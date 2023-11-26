#
# INVENTORY MANAGEMENT SYSTEM
#
# 23101291d Yang Xikun
# 23107919d Jin Qinhao
# 23101231d Jin Yixiao
# 23102145d Ren Yixiao
#
# A COMP1002 GROUP MINI PROJECT
# NOV 2023
#
# BUILD 1.0
#

# FILE FORMAT
import json
from PyQt5 import QtCore, QtGui, QtWidgets
import reportlab.platypus
import os
import sqlite3

# CLASSES
class Product:
    def __init__(self, name, price, quantity, supplier, id):
        self.name = name
        self.price = price
        self.quantity = quantity
        self.supplier = supplier
        self.id = id
    def serialize(self):
        return {
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "supplier": self.supplier,
            "id": self.id
        }
    @classmethod
    def deserialize(cls, data):
        return cls(data["name"], data["price"], data["quantity"], data["supplier"], data["id"])
class Transaction:
    def __init__(self, productID, productName, quantity, customer, date, profit):
        self.productID = productID
        self.productName = productName
        self.quantity = quantity
        self.customer = customer
        self.date = date
        self.profit = profit
    def serialize(self):
        return {
            "productID": self.productID,
            "productName": self.productName,
            "quantity": self.quantity,
            "customer": self.customer,
            "date": self.date,
            "profit": self.profit
        }
    @classmethod
    def deserialize(cls, data):
        return cls(data["productID"], data["productName"], data["quantity"], data["customer"], data["date"], data["profit"])

# INVENTORY MANAGEMENT SYSTEM
class InventoryManagementSystem(QtCore.QObject):
    shouldRefresh = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.products = []
        self.transactions = []

    def addProduct(self, name, price, quantity, supplier, id):
        for product in self.products:
            if product.id == id:
                return "ERROR"

        product = Product(name, price, quantity, supplier, id)
        self.products.append(product)
        self.products.sort(key=lambda product: product.id)
        self.shouldRefresh.emit()
        return "SUCCESS"

    def deleteProduct(self, id):
        for product in self.products:
            if (product.id == id):
                self.products.remove(product)
                break
        self.products.sort(key=lambda product: product.id)
        self.shouldRefresh.emit()

    def updateProduct(self, id, name=None, price=None, quantity=None, supplier=None):
        for product in self.products:
            if product.id == id:
                if name is not None:
                    product.name = name
                if price is not None:
                    product.price = price
                if quantity is not None:
                    product.quantity = quantity
                if supplier is not None:
                    product.supplier = supplier
        self.products.sort(key=lambda product: product.id)
        self.shouldRefresh.emit()

    def newTransaction(self, id, quantity, customer, date):
        for product in self.products:
            if product.id == id:
                if product.quantity >= quantity:
                    product.quantity -= quantity
                    transaction = Transaction(product.id, product.name, quantity, customer, date, product.price * quantity)
                    self.transactions.append(transaction)
                    self.transactions.sort(key=lambda transaction: transaction.productID)
                    self.shouldRefresh.emit()
                    return "SUCCESS"
                else:
                    return "ERROR_INSUFFICIENT"
        return "ERROR_ID_NOT_FOUND"

    # JSON
    def loadFromJSON(self, filename):
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
                self.products.clear()
                self.transactions.clear()
                for product in data["products"]:
                    self.products.append(Product.deserialize(product))
                for transaction in data["transactions"]:
                    self.transactions.append(Transaction.deserialize(transaction))
            self.shouldRefresh.emit()
            return "SUCCESS"
        except:
            return "ERROR"
    def saveToJSON(self, filename):
        data = {
            "products": [product.serialize() for product in self.products],
            "transactions": [transaction.serialize() for transaction in self.transactions]
        }
        with open(filename, 'w') as file:
            file.write(json.dumps(data))
        return "SUCCESS"

    # PDF
    def exportProductsListToPDF(self, filename):
        try:
            products_list = reportlab.platypus.SimpleDocTemplate(filename, pagesize=reportlab.lib.pagesizes.letter)
            ###
            style = reportlab.lib.styles.getSampleStyleSheet()
            titleStyle = style["Title"]
            title = reportlab.platypus.Paragraph("Products List", titleStyle)
            ###
            spacer = reportlab.platypus.Spacer(1, 10)
            ###
            data = [["Name", "Price", "Quantity", "Supplier", "ID"]]
            for product in self.products:
                data.append([product.name, product.price, product.quantity, product.supplier, product.id])
            table = reportlab.platypus.Table(data)
            table.setStyle(reportlab.platypus.TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), reportlab.lib.colors.white),
                ('TEXTCOLOR', (0, 0), (-1, 0), reportlab.lib.colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), reportlab.lib.colors.white),
                ('GRID', (0, 0), (-1, -1), 1, reportlab.lib.colors.black),
            ]))
            ###
            elements = [title, spacer, table]
            products_list.build(elements)
            ###
            return "SUCCESS"
        except:
            return "ERROR"
    def exportTransactionsReportToPDF(self, filename):
        try:
            transactions_report = reportlab.platypus.SimpleDocTemplate(filename, pagesize=reportlab.lib.pagesizes.letter)
            ###
            style = reportlab.lib.styles.getSampleStyleSheet()
            titleStyle = style["Title"]
            title = reportlab.platypus.Paragraph("Transactions Report", titleStyle)
            ###
            spacer = reportlab.platypus.Spacer(1, 10)
            ###
            data = [["Product Name", "Product ID", "Quantity", "Customer", "Transaction Date", "Profit"]]
            for transaction in self.transactions:
                data.append([transaction.productName, transaction.productID, transaction.quantity, transaction.customer, transaction.date, transaction.profit])
            table = reportlab.platypus.Table(data)
            table.setStyle(reportlab.platypus.TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), reportlab.lib.colors.white),
                ('TEXTCOLOR', (0, 0), (-1, 0), reportlab.lib.colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), reportlab.lib.colors.white),
                ('GRID', (0, 0), (-1, -1), 1, reportlab.lib.colors.black),
            ]))
            ###
            elements = [title, spacer, table]
            transactions_report.build(elements)
            ###
            return "SUCCESS"
        except:
            return "ERROR"

    # SQL
    def loadFromSQL(self, filename):
        self.products.clear()
        self.transactions.clear()
        ###
        try:
            if not os.path.exists(filename):
                return "ERROR"

            connectedDatabase = sqlite3.connect(filename)
            cursor = connectedDatabase.cursor()
            ###
            cursor.execute("SELECT * FROM products")
            productsFromDatabase = cursor.fetchall()
            for product in productsFromDatabase:
                name, price, quantity, supplier, id = product
                self.products.append(Product(name, price, quantity, supplier, id))
            ###
            cursor.execute("SELECT * FROM transactions")
            transactionsFromDatabase = cursor.fetchall()
            for transaction in transactionsFromDatabase:
                productID, productName, quantity, customer, date, profit = transaction
                self.transactions.append(Transaction(productID, productName, quantity, customer, date, profit))
            ###
            self.shouldRefresh.emit()
            ###
            return "SUCCESS"
        except:
            self.shouldRefresh.emit()
            return "ERROR"
    def saveToSQL(self, filename):
        try:
            connectedDatabase = sqlite3.connect(filename)
            cursor = connectedDatabase.cursor()
            ###
            cursor.execute('''CREATE TABLE IF NOT EXISTS products
                              (name TEXT,
                               price REAL,
                               quantity INTEGER,
                               supplier TEXT,
                               id INTEGER PRIMARY KEY)''')
            for product in self.products:
                cursor.execute('''INSERT INTO products
                                        (name, price, quantity, supplier, id)
                                        VALUES (?, ?, ?, ?, ?)''',
                               (product.name, product.price,
                                        product.quantity, product.supplier, product.id))
            ###
            cursor.execute('''CREATE TABLE IF NOT EXISTS transactions
                              (productID INTEGER,
                              productName TEXT,
                              quantity INTEGER,
                              customer TEXT,
                              date TEXT,
                              profit REAL)''')
            for transaction in self.transactions:
                cursor.execute('''INSERT INTO transactions
                                    (productID, productName, quantity, customer, date, profit)
                                    VALUES (?, ?, ?, ?, ?, ?)''',
                                   (transaction.productID, transaction.productName,
                                    transaction.quantity, transaction.customer,
                                    transaction.date, transaction.profit))
            ###
            connectedDatabase.commit()
            connectedDatabase.close()
            ###
            return "SUCCESS"
        except:
            self.shouldRefresh.emit()
            return "ERROR"

inventoryManagementSystem = InventoryManagementSystem()

class Divider(QtWidgets.QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QtWidgets.QFrame().HLine)
        self.setFrameShadow(QtWidgets.QFrame().Sunken)
        self.setStyleSheet("background-color: #888888; height: 1px; border-radius: 5px;")

class Spacer(QtWidgets.QLabel):
    def __init__(self):
        super().__init__()
        self.setText("")
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

class ErrorBox(QtWidgets.QMessageBox):
    def __init__(self, content):
        super().__init__()
        self.setIcon(QtWidgets.QMessageBox.Critical)
        self.setWindowTitle("ERROR")
        self.setText(content)
        self.setStandardButtons(QtWidgets.QMessageBox.Ok)

class SuccessBox(QtWidgets.QMessageBox):
    def __init__(self, content):
        super().__init__()
        self.setIcon(QtWidgets.QMessageBox.NoIcon)
        self.setWindowTitle("Action succeed!")
        self.setText(content)
        self.setStandardButtons(QtWidgets.QMessageBox.Ok)

# Table models
class ProductsTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data, headers=None, parent=None):
        super().__init__(parent)
        self.data = data
        self.headers = headers

    def rowCount(self, parent=None):
        return len(self.data)

    def columnCount(self, parent=None):
        return 6

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            col = index.column()
            product = self.data[row]

            if col == 0:
                return str(row + 1)
            elif col == 1:
                return product.name
            elif col == 2:
                return str(product.price)
            elif col == 3:
                return str(product.quantity)
            elif col == 4:
                return product.supplier
            elif col == 5:
                return str(product.id)

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal and self.headers is not None:
            if section == 1:
                return "Name"
            elif section == 2:
                return "Price"
            elif section == 3:
                return "Quantity"
            elif section == 4:
                return "Supplier"
            elif section == 5:
                return "ID"

class TransactionsTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data, headers=None, parent=None):
        super().__init__(parent)
        self.data = data
        self.headers = headers

    def rowCount(self, parent=None):
        return len(self.data)

    def columnCount(self, parent=None):
        return 7

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            col = index.column()
            transaction = self.data[row]

            if col == 0:
                return str(row + 1)
            elif col == 1:
                return transaction.productID
            elif col == 2:
                return str(transaction.productName)
            elif col == 3:
                return str(transaction.quantity)
            elif col == 4:
                return str(transaction.customer)
            elif col == 5:
                return str(transaction.date)
            elif col == 6:
                return str(transaction.profit)

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal and self.headers is not None:
            if section == 1:
                return "Product ID"
            elif section == 2:
                return "Product Name"
            elif section == 3:
                return "Quantity"
            elif section == 4:
                return "Customer"
            elif section == 5:
                return "Transaction Date"
            elif section == 6:
                return "Profit"

class Tables:
    def __init__(self):
        self.tablesLayout = QtWidgets.QHBoxLayout()
        # Products table
        self.productsTableContainer = QtWidgets.QVBoxLayout()
        self.productsTableLabel = QtWidgets.QLabel()
        self.productsTableLabel.setText("Products")
        self.productsTableLabel.setFont(QtGui.QFont("Helvetica", 16, QtGui.QFont.Bold))
        self.productsTable = QtWidgets.QTableView()
        self.productsTableModel = ProductsTableModel(inventoryManagementSystem.products, [])
        self.productsTable.setModel(self.productsTableModel)
        def updateProductsTableModel():
            self.productsTableModel.beginResetModel()
            self.productsTableModel.endResetModel()
        inventoryManagementSystem.shouldRefresh.connect(updateProductsTableModel)
        self.productsTable.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents) # ROW NUMBER
        self.productsTable.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents) # PRODUCT NAME
        self.productsTable.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents) # PRODUCT SUPPLIER
        self.productsTableContainer.addWidget(self.productsTableLabel)
        self.productsTableContainer.addWidget(self.productsTable)
        self.tablesLayout.addLayout(self.productsTableContainer)
        ###
        self.transactionsTableContainer = QtWidgets.QVBoxLayout()
        self.transactionsTableLabel = QtWidgets.QLabel()
        self.transactionsTableLabel.setText("Transactions")
        self.transactionsTableLabel.setFont(QtGui.QFont("Helvetica", 16, QtGui.QFont.Bold))
        self.transactionsTable = QtWidgets.QTableView()
        self.transactionsTableModel = TransactionsTableModel(inventoryManagementSystem.transactions, [])
        self.transactionsTable.setModel(self.transactionsTableModel)
        def upateTransactionsModel():
            self.transactionsTableModel.beginResetModel()
            self.transactionsTableModel.endResetModel()
        inventoryManagementSystem.shouldRefresh.connect(upateTransactionsModel)
        self.transactionsTable.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)  # ROW NUMBER
        self.transactionsTable.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)  # PRODUCT NAME
        self.transactionsTable.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)  # CUSTOMER
        self.transactionsTable.horizontalHeader().setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)  # TRANSACTION DATE
        self.transactionsTableContainer.addWidget(self.transactionsTableLabel)
        self.transactionsTableContainer.addWidget(self.transactionsTable)
        self.tablesLayout.addLayout(self.transactionsTableContainer)
    def getTables(self):
        return self.tablesLayout

class ProductWindow(QtWidgets.QMainWindow):
    shouldContinue = QtCore.pyqtSignal()

    def __init__(self, existingProduct, mode):
        super().__init__()
        self.setWindowTitle("Product")
        self.setFixedSize(500, 280)
        self.installEventFilter(self)

        self.productWindowLayout = QtWidgets.QVBoxLayout()
        ###
        self.productNameContainer = QtWidgets.QHBoxLayout()
        self.productNameContainer.addWidget(QtWidgets.QLabel("Name"))
        self.productNameEdit = QtWidgets.QLineEdit()
        self.productNameEdit.setPlaceholderText(existingProduct.name if (existingProduct != None) else "Name of the product")
        self.productNameEdit.setFixedWidth(400)
        self.productNameContainer.addWidget(self.productNameEdit)
        ###
        self.productPriceContainer = QtWidgets.QHBoxLayout()
        self.productPriceContainer.addWidget(QtWidgets.QLabel("Price"))
        self.productPriceEdit = QtWidgets.QLineEdit()
        self.productPriceEdit.setPlaceholderText(str(existingProduct.price) if (existingProduct != None) else "Price of the product")
        self.productPriceEdit.setFixedWidth(400)
        self.productPriceContainer.addWidget(self.productPriceEdit)
        ###
        self.productQuantityContainer = QtWidgets.QHBoxLayout()
        self.productQuantityContainer.addWidget(QtWidgets.QLabel("Quantity"))
        self.productQuantityEdit = QtWidgets.QLineEdit()
        self.productQuantityEdit.setPlaceholderText(str(existingProduct.quantity) if (existingProduct != None) else "Quantity of the product")
        self.productQuantityEdit.setFixedWidth(400)
        self.productQuantityContainer.addWidget(self.productQuantityEdit)
        ###
        self.productSupplierContainer = QtWidgets.QHBoxLayout()
        self.productSupplierContainer.addWidget(QtWidgets.QLabel("Supplier"))
        self.productSupplierEdit = QtWidgets.QLineEdit()
        self.productSupplierEdit.setPlaceholderText(existingProduct.supplier if (existingProduct != None) else "Supplier of the product")
        self.productSupplierEdit.setFixedWidth(400)
        self.productSupplierContainer.addWidget(self.productSupplierEdit)
        ###
        self.productIDContainer = QtWidgets.QHBoxLayout()
        self.productIDContainer.addWidget(QtWidgets.QLabel("ID"))
        self.productIDEdit = QtWidgets.QLineEdit()
        self.productIDEdit.setPlaceholderText(str(existingProduct.id) if (existingProduct != None) else "ID of the product")
        self.productIDEdit.setFixedWidth(400)
        self.productIDContainer.addWidget(self.productIDEdit)
        ###
        self.productOperationsContainer = QtWidgets.QHBoxLayout()
        self.cancelButton = QtWidgets.QPushButton()
        self.cancelButton.setText("Cancel")
        self.cancelButton.clicked.connect(self.close)
        self.doneButton = QtWidgets.QPushButton()
        self.doneButton.setText("Done")
        def doneButtonClicked():
            try:
                test1 = float(self.productPriceEdit.text()) if self.productPriceEdit.text() != "" else 0
                test2 = int(self.productQuantityEdit.text()) if self.productQuantityEdit.text() != "" else 0
                test3 = int(self.productIDEdit.text()) if self.productIDEdit.text() != "" else 0
            except:
                ErrorBox("Invalid data!").exec_()
                return

            if mode == "add":
                if self.productNameEdit.text() == "" or self.productPriceEdit.text() == "" or self.productQuantityEdit.text() == "" or self.productSupplierEdit.text() == "" or self.productIDEdit.text() == "":
                    ErrorBox("Incomplete data!").exec_()
                    return
                try:
                    if inventoryManagementSystem.addProduct(self.productNameEdit.text(), float(self.productPriceEdit.text()), int(self.productQuantityEdit.text()), self.productSupplierEdit.text(), int(self.productIDEdit.text())) == "SUCCESS":
                        SuccessBox("The product has been added successfully!").exec_()
                    else:
                        ErrorBox("Error! The system can't add the product!").exec_()
                except:
                    ErrorBox("Error! An unknown error occurred!").exec_()
            elif mode == "edit":
                if self.productNameEdit.text() != "":
                    existingProduct.name = self.productNameEdit.text()
                if self.productPriceEdit.text() != "":
                    existingProduct.price = float(self.productPriceEdit.text())
                if self.productQuantityEdit.text() != "":
                    existingProduct.quantity = int(self.productQuantityEdit.text())
                if self.productSupplierEdit.text() != "":
                    existingProduct.supplier = self.productSupplierEdit.text()
                if self.productIDEdit.text() != "":
                    existingProduct.id = self.productIDEdit.text()
                SuccessBox("Success!").exec_()
            self.close()
        self.doneButton.clicked.connect(doneButtonClicked)
        self.productOperationsContainer.addWidget(self.cancelButton)
        self.productOperationsContainer.addWidget(self.doneButton)
        ###
        self.productWindowLayout.addLayout(self.productNameContainer)
        self.productWindowLayout.addLayout(self.productPriceContainer)
        self.productWindowLayout.addLayout(self.productQuantityContainer)
        self.productWindowLayout.addLayout(self.productSupplierContainer)
        self.productWindowLayout.addLayout(self.productIDContainer)
        self.productWindowLayout.addLayout(self.productOperationsContainer)
        ###
        self.productWindowWidget = QtWidgets.QWidget()
        self.productWindowWidget.setLayout(self.productWindowLayout)
        self.setCentralWidget(self.productWindowWidget)
        ###
        self.shouldContinue.connect(doneButtonClicked)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            self.shouldContinue.emit()

class SearchingIDWindow(QtWidgets.QMainWindow):
    shouldContinue = QtCore.pyqtSignal()

    def __init__(self, mode):
        super().__init__()
        self.setWindowTitle("Searching by Product ID")
        self.setFixedSize(500, 120)

        self.searchingIDWindowLayout = QtWidgets.QVBoxLayout()

        ###
        self.productIDContainer = QtWidgets.QHBoxLayout()
        self.productIDContainer.addWidget(QtWidgets.QLabel("Product ID"))
        self.productIDEdit = QtWidgets.QLineEdit()
        self.productIDEdit.setPlaceholderText("ID of the product")
        self.productIDEdit.setFixedWidth(400)
        self.productIDContainer.addWidget(self.productIDEdit)
        ###
        self.operationsContainer = QtWidgets.QHBoxLayout()
        self.cancelButton = QtWidgets.QPushButton()
        self.cancelButton.setText("Cancel")
        self.cancelButton.clicked.connect(self.close)
        self.doneButton = QtWidgets.QPushButton()
        self.doneButton.setText("Go to edit" if (mode == "edit") else "Delete")
        def searchButtonClicked():
            try:
                test = int(self.productIDEdit.text()) if self.productIDEdit.text() != "" else 0
            except:
                ErrorBox("Invalid data!").exec_()
                return

            if self.productIDEdit.text() == "":
                ErrorBox("Erorr, no product ID input!").exec_()
                return
            exists = False
            for product in inventoryManagementSystem.products:
                if product.id == int(self.productIDEdit.text()):
                    exists = True
                    if mode == "edit":
                        ProductWindow(product, "edit").show()
                    elif mode == "delete":
                        inventoryManagementSystem.deleteProduct(product.id)
                        SuccessBox("The product has been deleted!").exec_()
                    self.close()
                    break
            if exists == False:
                ErrorBox("Error! No product with such ID: " + self.productIDEdit.text() + " found!").exec_()

        self.doneButton.clicked.connect(searchButtonClicked)
        self.operationsContainer.addWidget(self.cancelButton)
        self.operationsContainer.addWidget(self.doneButton)
        ###
        self.searchingIDWindowLayout.addLayout(self.productIDContainer)
        self.searchingIDWindowLayout.addLayout(self.operationsContainer)
        ###
        self.searchingIDWindowWidget = QtWidgets.QWidget()
        self.searchingIDWindowWidget.setLayout(self.searchingIDWindowLayout)
        self.setCentralWidget(self.searchingIDWindowWidget)
        ###
        self.shouldContinue.connect(searchButtonClicked)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            self.shouldContinue.emit()

class TransactionWindow(QtWidgets.QMainWindow):
    shouldContinue = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Transaction")
        self.setFixedSize(500, 230)

        self.transactionWindowLayout = QtWidgets.QVBoxLayout()
        ###
        self.productIDContainer = QtWidgets.QHBoxLayout()
        self.productIDContainer.addWidget(QtWidgets.QLabel("Product ID"))
        self.productIDEdit = QtWidgets.QLineEdit()
        self.productIDEdit.setPlaceholderText("ID of the product")
        self.productIDEdit.setFixedWidth(400)
        self.productIDContainer.addWidget(self.productIDEdit)
        ###
        self.productQuantityContainer = QtWidgets.QHBoxLayout()
        self.productQuantityContainer.addWidget(QtWidgets.QLabel("Quantity"))
        self.productQuantityEdit = QtWidgets.QLineEdit()
        self.productQuantityEdit.setPlaceholderText("Quantity of the product")
        self.productQuantityEdit.setFixedWidth(400)
        self.productQuantityContainer.addWidget(self.productQuantityEdit)
        ###
        self.customerContainer = QtWidgets.QHBoxLayout()
        self.customerContainer.addWidget(QtWidgets.QLabel("Customer"))
        self.customerEdit = QtWidgets.QLineEdit()
        self.customerEdit.setPlaceholderText("Customer of the transaction")
        self.customerEdit.setFixedWidth(400)
        self.customerContainer.addWidget(self.customerEdit)
        ###
        self.transactionDateContainer = QtWidgets.QHBoxLayout()
        self.transactionDateContainer.addWidget(QtWidgets.QLabel("Date"))
        self.transactionDateEdit = QtWidgets.QLineEdit()
        self.transactionDateEdit.setPlaceholderText("Date of the transaction")
        self.transactionDateEdit.setFixedWidth(400)
        self.transactionDateContainer.addWidget(self.transactionDateEdit)
        ###
        self.transactionOperationsContainer = QtWidgets.QHBoxLayout()
        self.cancelButton = QtWidgets.QPushButton()
        self.cancelButton.setText("Cancel")
        self.cancelButton.clicked.connect(self.close)
        self.doneButton = QtWidgets.QPushButton()
        self.doneButton.setText("Done")
        def doneButtonClicked():
            if self.productIDEdit.text() == "" or self.productQuantityEdit.text() == "" or self.customerEdit.text() == "" or self.transactionDateEdit.text() == "":
                ErrorBox("Incomplete data!").exec_()
                return
            try:
                newTransaction = inventoryManagementSystem.newTransaction(int(self.productIDEdit.text()), int(self.productQuantityEdit.text()), self.customerEdit.text(), self.transactionDateEdit.text())
                if newTransaction == "ERROR_ID_NOT_FOUND":
                    ErrorBox("Error! ID not found!").exec_()
                    return
                elif newTransaction == "ERROR_INSUFFICIENT":
                    ErrorBox("Error! Quantity insufficient!").exec_()
                    return
                elif newTransaction == "SUCCESS":
                    SuccessBox("A new transaction has been made successfully!").exec_()
            except:
                ErrorBox("Error! An unknown error occurred!").exec_()
            self.close()
        self.doneButton.clicked.connect(doneButtonClicked)
        self.transactionOperationsContainer.addWidget(self.cancelButton)
        self.transactionOperationsContainer.addWidget(self.doneButton)
        ###
        self.transactionWindowLayout.addLayout(self.productIDContainer)
        self.transactionWindowLayout.addLayout(self.productQuantityContainer)
        self.transactionWindowLayout.addLayout(self.customerContainer)
        self.transactionWindowLayout.addLayout(self.transactionDateContainer)
        self.transactionWindowLayout.addLayout(self.transactionOperationsContainer)
        ###
        self.transactionWindowWidget = QtWidgets.QWidget()
        self.transactionWindowWidget.setLayout(self.transactionWindowLayout)
        self.setCentralWidget(self.transactionWindowWidget)
        ###
        self.shouldContinue.connect(doneButtonClicked)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            self.shouldContinue.emit()

class FilenameWindow(QtWidgets.QMainWindow):
    shouldContinue = QtCore.pyqtSignal()

    def __init__(self, mode):
        super().__init__()
        self.setWindowTitle("File name")
        self.setFixedSize(500, 120)
        self.filenameWindowLayout = QtWidgets.QVBoxLayout()
        ###
        self.filenameContainer = QtWidgets.QHBoxLayout()
        self.filenameContainer.addWidget(QtWidgets.QLabel("File name"))
        self.filenameEdit = QtWidgets.QLineEdit()
        self.filenameEdit.setFixedWidth(400)
        self.filenameContainer.addWidget(self.filenameEdit)
        ###
        self.operationsContainer = QtWidgets.QHBoxLayout()
        #
        self.cancelButton = QtWidgets.QPushButton()
        self.cancelButton.setText("Cancel")
        self.cancelButton.clicked.connect(self.close)
        #
        self.doneButton = QtWidgets.QPushButton()
        if mode == "save_json" or mode == "save_sql":
            self.doneButton.setText("Save")
        elif mode == "load_json" or mode == "load_sql":
            self.doneButton.setText("Load")
        elif mode == "pdf_export_products_list" or mode == "pdf_export_transactions_report":
            self.doneButton.setText("Export")
        #
        def doneButtonClicked():
            if self.filenameEdit.text() == "":
                ErrorBox("Invalid filename!").exec_()
                return

            hasExtension = False
            for i in range(0, len(self.filenameEdit.text())):
                if self.filenameEdit.text()[i] == '.' and i <= len(self.filenameEdit.text()) - 1:
                    hasExtension = True
                    break
            if hasExtension == False:
                ErrorBox("No file extension!").exec_()
                return
            try:
                if mode == "load_json":
                    if inventoryManagementSystem.loadFromJSON(self.filenameEdit.text()) == "SUCCESS":
                        SuccessBox("JSON file successfully loaded!").exec_()
                    else:
                        ErrorBox("Error! Unable to load JSON file!").exec_()
                elif mode == "save_json":
                    if inventoryManagementSystem.saveToJSON(self.filenameEdit.text()) == "SUCCESS":
                        SuccessBox("JSON file successfully saved!").exec_()
                    else:
                        ErrorBox("Error! Invalid inventory information!")
                ###
                elif mode == "load_sql":
                    if inventoryManagementSystem.loadFromSQL(self.filenameEdit.text()) == "SUCCESS":
                        SuccessBox("SQL file successfully loaded!").exec_()
                    else:
                        ErrorBox("Error! Unable to load SQL database file!").exec_()
                elif mode == "save_sql":
                    if inventoryManagementSystem.saveToSQL(self.filenameEdit.text()) == "SUCCESS":
                        SuccessBox("SQL file successfully saved!").exec_()
                    else:
                        ErrorBox("Error! Unable to save SQL file!").exec_()
                ###
                elif mode == "pdf_export_products_list":
                    if len(inventoryManagementSystem.products) == 0:
                        ErrorBox("No products!").exec_()
                    try:
                        if inventoryManagementSystem.exportProductsListToPDF(self.filenameEdit.text()) == "SUCCESS":
                            SuccessBox("The products list has been successfully exported to PDF file!").exec_()
                        else:
                            ErrorBox("Error! Unable to export the PDF file!").exec_()
                    except:
                        ErrorBox("Error! An unknown error occurred!").exec_()
                elif mode == "pdf_export_transactions_report":
                    if len(inventoryManagementSystem.transactions) == 0:
                        ErrorBox("No transactions!").exec_()
                    try:
                        if inventoryManagementSystem.exportTransactionsReportToPDF(self.filenameEdit.text()) == "SUCCESS":
                            SuccessBox("The transactions report has been successfully exported to PDF file!").exec_()
                        else:
                            ErrorBox("Error! Unable to export the PDF file!").exec_()
                    except:
                        ErrorBox("Error! An unknown error occurred!").exec_()
            except:
                ErrorBox("Error! An unknown error occurred!")
            self.close()
        self.doneButton.clicked.connect(doneButtonClicked)
        #
        self.operationsContainer.addWidget(self.cancelButton)
        self.operationsContainer.addWidget(self.doneButton)
        ###
        self.filenameWindowLayout.addLayout(self.filenameContainer)
        self.filenameWindowLayout.addLayout(self.operationsContainer)
        ###
        self.filenameWindowWidget = QtWidgets.QWidget()
        self.filenameWindowWidget.setLayout(self.filenameWindowLayout)
        self.setCentralWidget(self.filenameWindowWidget)
        ###
        self.shouldContinue.connect(doneButtonClicked)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            self.shouldContinue.emit()

class Sidebar:
    def __init__(self):
        # Sidebar
        self.sidebarLayout = QtWidgets.QVBoxLayout()
        # Sidebar buttons
        self.addProductButton = QtWidgets.QPushButton("Add a new product")
        self.addProductButton.clicked.connect(lambda: ProductWindow(None, "add").show())
        ###
        self.editProductButton = QtWidgets.QPushButton("Edit a product")
        self.editProductButton.clicked.connect(lambda: SearchingIDWindow("edit").show())
        ###
        self.deleteProductButton = QtWidgets.QPushButton("Delete a product")
        self.deleteProductButton.clicked.connect(lambda: SearchingIDWindow("delete").show())
        ###
        self.newTransactionButton = QtWidgets.QPushButton("Make a new transaction")
        self.newTransactionButton.clicked.connect(lambda: TransactionWindow().show())
        ###
        self.loadFromJSONButton = QtWidgets.QPushButton("Load from JSON file")
        self.loadFromJSONButton.clicked.connect(lambda: FilenameWindow("load_json").show())
        ###
        self.saveToJSONButton = QtWidgets.QPushButton("Save to JSON file")
        self.saveToJSONButton.clicked.connect(lambda: FilenameWindow("save_json").show())
        ###
        self.exportProductsListAsPDF = QtWidgets.QPushButton("PDF products list")
        self.exportProductsListAsPDF.clicked.connect(lambda: FilenameWindow("pdf_export_products_list").show())
        ###
        self.exportTransactionsReportAsPDF = QtWidgets.QPushButton("PDF transactions report")
        self.exportTransactionsReportAsPDF.clicked.connect(lambda: FilenameWindow("pdf_export_transactions_report").show())
        ###
        self.loadFromSQLButton = QtWidgets.QPushButton("Load from SQL file")
        self.loadFromSQLButton.clicked.connect(lambda: FilenameWindow("load_sql").show())
        ###
        self.saveToSQLButton = QtWidgets.QPushButton("Save to SQL file")
        self.saveToSQLButton.clicked.connect(lambda: FilenameWindow("save_sql").show())
        ###
        self.sidebarLayout.addWidget(QtWidgets.QLabel("Products"))
        self.sidebarLayout.addWidget(self.addProductButton)
        self.sidebarLayout.addWidget(self.editProductButton)
        self.sidebarLayout.addWidget(self.deleteProductButton)
        self.sidebarLayout.addWidget(Divider())
        self.sidebarLayout.addWidget(QtWidgets.QLabel("Transactions"))
        self.sidebarLayout.addWidget(self.newTransactionButton)
        self.sidebarLayout.addWidget(Divider())
        self.sidebarLayout.addWidget(QtWidgets.QLabel("JSON file loads"))
        self.sidebarLayout.addWidget(self.loadFromJSONButton)
        self.sidebarLayout.addWidget(self.saveToJSONButton)
        self.sidebarLayout.addWidget(Divider())
        self.sidebarLayout.addWidget(QtWidgets.QLabel("PDF exports"))
        self.sidebarLayout.addWidget(self.exportProductsListAsPDF)
        self.sidebarLayout.addWidget(self.exportTransactionsReportAsPDF)
        self.sidebarLayout.addWidget(Divider())
        self.sidebarLayout.addWidget(QtWidgets.QLabel("SQL file loads"))
        self.sidebarLayout.addWidget(self.loadFromSQLButton)
        self.sidebarLayout.addWidget(self.saveToSQLButton)
        self.sidebarLayout.addWidget(Spacer())

        # AUTHORS
        self.sidebarLayout.addWidget(QtWidgets.QLabel("Group 0000000 Gyrfalcon"))
        self.sidebarLayout.addWidget(QtWidgets.QLabel("23101291d Yang Xikun"))
        self.sidebarLayout.addWidget(QtWidgets.QLabel("23107919d Jin Qinhao"))
        self.sidebarLayout.addWidget(QtWidgets.QLabel("23101231d Jin Yixiao"))
        self.sidebarLayout.addWidget(QtWidgets.QLabel("23102145d Ren Yixiao"))
    def getSidebar(self):
        return self.sidebarLayout

class IMSAppWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Management System")
        self.showMaximized()
        ###
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(Sidebar().getSidebar())
        self.layout.addLayout(Tables().getTables())
        ###
        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

# PROGRAM START
# Codes before this __main__ function will also be executed.
if __name__ == "__main__":
    InventoryManagementSystemApplication = QtWidgets.QApplication([])
    imsAppWindow = IMSAppWindow()
    imsAppWindow.show()
    InventoryManagementSystemApplication.exec_()
# Program ends.

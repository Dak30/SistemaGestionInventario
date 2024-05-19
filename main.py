import sqlite3

def inicializar_db():
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Categoria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        descripcion TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Proveedor (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        direccion TEXT,
        telefono TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Bodega (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        ubicacion TEXT,
        capacidad_maxima INTEGER
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Producto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        precio REAL,
        stock INTEGER,
        categoria_id INTEGER,
        proveedor_id INTEGER,
        bodega_id INTEGER,
        FOREIGN KEY (categoria_id) REFERENCES Categoria(id),
        FOREIGN KEY (proveedor_id) REFERENCES Proveedor(id),
        FOREIGN KEY (bodega_id) REFERENCES Bodega(id)
    )
    ''')

    conn.commit()
    conn.close()

def agregar_categoria(nombre, descripcion):
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Categoria (nombre, descripcion) VALUES (?, ?)", (nombre, descripcion))
    conn.commit()
    conn.close()

def agregar_proveedor(nombre, direccion, telefono, productos):
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Proveedor (nombre, direccion, telefono) VALUES (?, ?, ?)", (nombre, direccion, telefono))
    proveedor_id = cursor.lastrowid
    for producto in productos:
        cursor.execute('''
        UPDATE Producto SET proveedor_id = ? WHERE nombre = ?
        ''', (proveedor_id, producto))
    conn.commit()
    conn.close()

def agregar_bodega(nombre, ubicacion, capacidad_maxima, productos):
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Bodega (nombre, ubicacion, capacidad_maxima) VALUES (?, ?, ?)", (nombre, ubicacion, capacidad_maxima))
    bodega_id = cursor.lastrowid
    for producto in productos:
        cursor.execute('''
        UPDATE Producto SET bodega_id = ? WHERE nombre = ?
        ''', (bodega_id, producto))
    conn.commit()
    conn.close()

def agregar_producto(nombre, descripcion, precio, stock, categoria_id, proveedor_id, bodega_id):
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO Producto (nombre, descripcion, precio, stock, categoria_id, proveedor_id, bodega_id) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (nombre, descripcion, precio, stock, categoria_id, proveedor_id, bodega_id))
    conn.commit()
    conn.close()

def eliminar_producto(nombre):
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Producto WHERE nombre = ?", (nombre,))
    conn.commit()
    conn.close()

def agregar_producto_a_categoria(producto_nombre, categoria_id):
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE Producto SET categoria_id = ? WHERE nombre = ?
    ''', (categoria_id, producto_nombre))
    conn.commit()
    conn.close()

def eliminar_producto_de_categoria(producto_nombre):
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE Producto SET categoria_id = NULL WHERE nombre = ?
    ''', (producto_nombre,))
    conn.commit()
    conn.close()

def agregar_producto_a_proveedor(producto_nombre, proveedor_id):
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE Producto SET proveedor_id = ? WHERE nombre = ?
    ''', (proveedor_id, producto_nombre))
    conn.commit()
    conn.close()

def eliminar_producto_de_proveedor(producto_nombre):
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE Producto SET proveedor_id = NULL WHERE nombre = ?
    ''', (producto_nombre,))
    conn.commit()
    conn.close()

def agregar_producto_a_bodega(producto_nombre, bodega_id):
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT SUM(stock) FROM Producto WHERE bodega_id = ?
    ''', (bodega_id,))
    total_stock_bodega = cursor.fetchone()[0] or 0

    cursor.execute('''
    SELECT capacidad_maxima FROM Bodega WHERE id = ?
    ''', (bodega_id,))
    capacidad_maxima = cursor.fetchone()[0]

    cursor.execute('''
    SELECT stock FROM Producto WHERE nombre = ?
    ''', (producto_nombre,))
    producto_stock = cursor.fetchone()[0]

    if total_stock_bodega + producto_stock <= capacidad_maxima:
        cursor.execute('''
        UPDATE Producto SET bodega_id = ? WHERE nombre = ?
        ''', (bodega_id, producto_nombre))
        conn.commit()
    else:
        print("No hay suficiente espacio en la bodega.")
    conn.close()

def retirar_producto_de_bodega(producto_nombre, cantidad):
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT stock FROM Producto WHERE nombre = ?
    ''', (producto_nombre,))
    stock_actual = cursor.fetchone()[0]

    if stock_actual >= cantidad:
        cursor.execute('''
        UPDATE Producto SET stock = stock - ? WHERE nombre = ?
        ''', (cantidad, producto_nombre))
        conn.commit()
    else:
        print("No hay suficiente stock disponible.")
    conn.close()

def consultar_disponibilidad_producto_bodega(producto_nombre, bodega_id):
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT stock FROM Producto WHERE nombre = ? AND bodega_id = ?
    ''', (producto_nombre, bodega_id))
    stock = cursor.fetchone()
    conn.close()
    return stock[0] if stock else 0

def consultar_producto(nombre):
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT p.nombre, p.descripcion, p.precio, p.stock, c.nombre, pr.nombre, b.nombre
    FROM Producto p
    LEFT JOIN Categoria c ON p.categoria_id = c.id
    LEFT JOIN Proveedor pr ON p.proveedor_id = pr.id
    LEFT JOIN Bodega b ON p.bodega_id = b.id
    WHERE p.nombre = ?
    ''', (nombre,))
    producto = cursor.fetchone()
    conn.close()
    return producto

def consultar_categoria(nombre):
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id, nombre, descripcion FROM Categoria WHERE nombre = ?
    ''', (nombre,))
    categoria = cursor.fetchone()
    if categoria:
        cursor.execute('''
        SELECT nombre FROM Producto WHERE categoria_id = ?
        ''', (categoria[0],))
        productos = cursor.fetchall()
    else:
        productos = []
    conn.close()
    return categoria, productos

def consultar_proveedor(nombre):
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id, nombre, direccion, telefono FROM Proveedor WHERE nombre = ?
    ''', (nombre,))
    proveedor = cursor.fetchone()
    if proveedor:
        cursor.execute('''
        SELECT nombre FROM Producto WHERE proveedor_id = ?
        ''', (proveedor[0],))
        productos = cursor.fetchall()
    else:
        productos = []
    conn.close()
    return proveedor, productos

def consultar_bodega(nombre):
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id, nombre, ubicacion, capacidad_maxima FROM Bodega WHERE nombre = ?
    ''', (nombre,))
    bodega = cursor.fetchone()
    if bodega:
        cursor.execute('''
        SELECT nombre FROM Producto WHERE bodega_id = ?
        ''', (bodega[0],))
        productos = cursor.fetchall()
    else:
        productos = []
    conn.close()
    return bodega, productos

def informe_stock_total():
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(stock) FROM Producto')
    total_stock = cursor.fetchone()[0]
    conn.close()
    return total_stock

def informe_stock_por_categoria():
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT c.nombre, SUM(p.stock)
    FROM Producto p
    JOIN Categoria c ON p.categoria_id = c.id
    GROUP BY c.nombre
    ''')
    informe = cursor.fetchall()
    conn.close()
    return informe

def informe_stock_por_proveedor():
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT pr.nombre, SUM(p.stock)
    FROM Producto p
    JOIN Proveedor pr ON p.proveedor_id = pr.id
    GROUP BY pr.nombre
    ''')
    informe = cursor.fetchall()
    conn.close()
    return informe

def informe_stock_por_bodega():
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT b.nombre, SUM(p.stock)
    FROM Producto p
    JOIN Bodega b ON p.bodega_id = b.id
    GROUP BY b.nombre
    ''')
    informe = cursor.fetchall()
    conn.close()
    return informe

def menu():
    while True:
        print("\nSistema de Gestión de Inventario")
        print("1. Agregar Categoría")
        print("2. Agregar Proveedor")
        print("3. Agregar Bodega")
        print("4. Agregar Producto")
        print("5. Eliminar Producto")
        print("6. Agregar Producto a Categoría")
        print("7. Eliminar Producto de Categoría")
        print("8. Agregar Producto a Proveedor")
        print("9. Eliminar Producto de Proveedor")
        print("10. Agregar Producto a Bodega")
        print("11. Retirar Producto de Bodega")
        print("12. Consultar Disponibilidad de Producto en Bodega")
        print("13. Consultar Producto")
        print("14. Consultar Categoría")
        print("15. Consultar Proveedor")
        print("16. Consultar Bodega")
        print("17. Informe de Stock")
        print("18. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            nombre = input("Ingrese el nombre de la categoría: ")
            descripcion = input("Ingrese la descripción de la categoría: ")
            agregar_categoria(nombre, descripcion)
            print("Categoría agregada exitosamente.")

        elif opcion == '2':
            nombre = input("Ingrese el nombre del proveedor: ")
            direccion = input("Ingrese la dirección del proveedor: ")
            telefono = input("Ingrese el teléfono del proveedor: ")
            productos = input("Ingrese los productos suministrados (separados por comas): ").split(',')
            agregar_proveedor(nombre, direccion, telefono, [producto.strip() for producto in productos])
            print("Proveedor agregado exitosamente.")

        elif opcion == '3':
            nombre = input("Ingrese el nombre de la bodega: ")
            ubicacion = input("Ingrese la ubicación de la bodega: ")
            capacidad_maxima = int(input("Ingrese la capacidad máxima de la bodega: "))
            productos = input("Ingrese los productos almacenados (separados por comas): ").split(',')
            agregar_bodega(nombre, ubicacion, capacidad_maxima, [producto.strip() for producto in productos])
            print("Bodega agregada exitosamente.")

        elif opcion == '4':
            nombre = input("Ingrese el nombre del producto: ")
            descripcion = input("Ingrese la descripción del producto: ")
            precio = float(input("Ingrese el precio del producto: "))
            stock = int(input("Ingrese el stock del producto: "))
            categoria_id = int(input("Ingrese el ID de la categoría del producto: "))
            proveedor_id = int(input("Ingrese el ID del proveedor del producto (opcional, presione Enter si no tiene): ") or 0)
            bodega_id = int(input("Ingrese el ID de la bodega del producto (opcional, presione Enter si no tiene): ") or 0)
            agregar_producto(nombre, descripcion, precio, stock, categoria_id, proveedor_id, bodega_id)
            print("Producto agregado exitosamente.")

        elif opcion == '5':
            nombre = input("Ingrese el nombre del producto: ")
            eliminar_producto(nombre)
            print("Producto eliminado exitosamente.")

        elif opcion == '6':
            producto_nombre = input("Ingrese el nombre del producto: ")
            categoria_id = int(input("Ingrese el ID de la categoría: "))
            agregar_producto_a_categoria(producto_nombre, categoria_id)
            print("Producto agregado a la categoría exitosamente.")

        elif opcion == '7':
            producto_nombre = input("Ingrese el nombre del producto: ")
            eliminar_producto_de_categoria(producto_nombre)
            print("Producto eliminado de la categoría exitosamente.")

        elif opcion == '8':
            producto_nombre = input("Ingrese el nombre del producto: ")
            proveedor_id = int(input("Ingrese el ID del proveedor: "))
            agregar_producto_a_proveedor(producto_nombre, proveedor_id)
            print("Producto agregado al proveedor exitosamente.")

        elif opcion == '9':
            producto_nombre = input("Ingrese el nombre del producto: ")
            eliminar_producto_de_proveedor(producto_nombre)
            print("Producto eliminado del proveedor exitosamente.")

        elif opcion == '10':
            producto_nombre = input("Ingrese el nombre del producto: ")
            bodega_id = int(input("Ingrese el ID de la bodega: "))
            agregar_producto_a_bodega(producto_nombre, bodega_id)
            print("Producto agregado a la bodega exitosamente.")

        elif opcion == '11':
            producto_nombre = input("Ingrese el nombre del producto: ")
            cantidad = int(input("Ingrese la cantidad a retirar: "))
            retirar_producto_de_bodega(producto_nombre, cantidad)
            print("Producto retirado de la bodega exitosamente.")

        elif opcion == '12':
            producto_nombre = input("Ingrese el nombre del producto: ")
            bodega_id = int(input("Ingrese el ID de la bodega: "))
            disponibilidad = consultar_disponibilidad_producto_bodega(producto_nombre, bodega_id)
            print(f"Disponibilidad del producto en la bodega: {disponibilidad}")

        elif opcion == '13':
            nombre = input("Ingrese el nombre del producto: ")
            producto = consultar_producto(nombre)
            if producto:
                print("Producto encontrado:", producto)
            else:
                print("Producto no encontrado.")

        elif opcion == '14':
            nombre = input("Ingrese el nombre de la categoría: ")
            categoria, productos = consultar_categoria(nombre)
            if categoria:
                print("Categoría encontrada:", categoria)
                print("Productos asociados:", productos)
            else:
                print("Categoría no encontrada.")

        elif opcion == '15':
            nombre = input("Ingrese el nombre del proveedor: ")
            proveedor, productos = consultar_proveedor(nombre)
            if proveedor:
                print("Proveedor encontrado:", proveedor)
                print("Productos asociados:", productos)
            else:
                print("Proveedor no encontrado.")

        elif opcion == '16':
            nombre = input("Ingrese el nombre de la bodega: ")
            bodega, productos = consultar_bodega(nombre)
            if bodega:
                print("Bodega encontrada:", bodega)
                print("Productos almacenados:", productos)
            else:
                print("Bodega no encontrada.")

        elif opcion == '17':
            print("Seleccione el tipo de informe de stock:")
            print("1. Stock Total")
            print("2. Stock por Categoría")
            print("3. Stock por Proveedor")
            print("4. Stock por Bodega")

            tipo_informe = input("Seleccione una opción: ")

            if tipo_informe == '1':
                print("Stock total:", informe_stock_total())
            elif tipo_informe == '2':
                informe = informe_stock_por_categoria()
                for categoria, stock in informe:
                    print(f"{categoria}: {stock}")
            elif tipo_informe == '3':
                informe = informe_stock_por_proveedor()
                for proveedor, stock in informe:
                    print(f"{proveedor}: {stock}")
            elif tipo_informe == '4':
                informe = informe_stock_por_bodega()
                for bodega, stock in informe:
                    print(f"{bodega}: {stock}")
            else:
                print("Opción no válida.")

        elif opcion == '18':
            print("Saliendo del sistema.")
            break

        else:
            print("Opción no válida. Intente nuevamente.")

# Ejemplo de uso
if __name__ == "__main__":
    inicializar_db()
    menu()

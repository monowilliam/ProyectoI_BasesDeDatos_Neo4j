from py2neo import Graph, Node, Relationship #libreria de py2neo, aquella que permite definicion de cada componente de esta y coneccion con la db
import  os,time #importadas para comandos en sistema
m=Graph("http://194.182.87.136:7474",host="194.182.87.136",password="bases12345")#se realiza la coneccion a la base de datos local con atributos con contraseña, esto extrae un grafo al cual llamamos m 
class usuario:
    username=""
    usermode=""
    ciudad=""
    userfollows=[]
    followers=[]
    invitations=[]
    def __init__(self, n,p):
        self.username=n
        self.usermode=p
    def setusername(self,n):
        self.username=n
    def setusermode(self):
        if(self.usermode=="Publico"):
            self.usermode="Privado"
        else:
            self.usermode="Publico"
    def getusername(self):
        return self.username
    def getusermode(self):
        return self.usermode
    def setnewfollower(self,user):
        if(not(user in self.followers)):
            self.followers.append(user)
    def getfollowers(self):
        return self.followers
    def setnewfollowed(self,user):
        if(not(user in self.userfollows)):
            self.userfollows.append(user)
    def getfollowed(self):
        return self.userfollows
    def getinvitations(self):
        return self.invitations
    def setnewinvitation(self,user):
        if(not(user in self.invitations)):
            self.invitations.append(user)
    def setciudad(self,n):
        self.ciudad=n
    def getciudad(self):
        return self.ciudad
def mostrar_seguidores(user):
    """
Funcion que se encarga de mostrar los seguidores del usuario, imprimiendolos linea por linea.
    """
    while(True):
        if(len(user.getfollowers())!=0):
            for x in user.getfollowers():
                print(x)
                print('\n')
        else:
            print("Usted aun no es sequido por alguien.")
        if(int(input("Cerrar? 1:si\t0:no"))):
            os.system('cls')
            break
        else:os.system('cls')
def mostrar_seguidos(user):
    """
Funcion que se encarga de mostrar los usuarios que sigue el usuario, imprimiendolos linea por linea.
    """
    while(True):
        if(len(user.getfollowed())!=0):
            for x in user.getfollowed():
                print(x)
                print('\n')
        else:
            print("Usted aun no sigue a nadie.")
        if(int(input("Cerrar? 1:si\t0:no"))):
            os.system('cls')
            break
        else:os.system('cls')
def mostrar_invitaciones(user):
    """
Funcion que se encarga de mostrar las solicitudes de amistad pendientes que el usuario posee,
se muestra un listado de los usuarios que las realizan y opcion de aceptarlas, al aceptarlas
se realiza una busqueda de su relacion para cambiar sus propiedades y volverlo un seguidor mas.
    """
    while(True):
        if(len(user.getinvitations())!=0):
            for x in user.getinvitations():
                print(str(x)+":"+str(user.getinvitations().index(x)+1)+'\n')
            o=int(input("Desea aceptar alguna? 0:no\t1-"+str(len(user.getinvitations()))+":persona a aceptar solicitud\n"))
            if(o!=0):
                m.run("MATCH (b:usuario)-[r:follows {estado:['0']}]->(a:usuario) WHERE a.nombreu='"+user.getusername()+"' and b.nombreu='"+user.getinvitations()[o-1]+"' SET r.estado =['1']")#cambia la propiedad estado de la relacion follows de 0 a 1(es seguidor) 
                user.setnewfollower(user.getinvitations()[o-1])#se agrega a los seguidores a nivel de objetos
                user.getinvitations().pop(o-1)#se elimina a nivel de objetos su nombre de las invitaciones
                os.system('cls')
                continue
            else:
                os.system('cls')
                break
                
        else:
            print("Usted no tiene solicitudes de amistad.")
            break
def vertweetsRecibidos(node, user): #retorna todos los tweets en los que aparece como destinatario
    dic=m.run("MATCH (a)-[:enviaa]->(b) WHERE b.nombreu = '"+user.getusername()+"' RETURN a").data()
    if(len(dic)==0):
        print("Aun no has recibido ningun tweet.\n")
        time.sleep(5)
        os.system('cls')
    else:
        for x in dic:
            for i in x.keys():
                print(str(x[i]['fecha'])+"\n"+str(x[i]['texto'])+"\n-----------------------------------------------")
                if (int(input("Cerrar? \n 1:si\n 2:no\n"))):
                    os.system('cls')
                    break
                else:
                    os.system('cls')
            

def realizartweet(user,node): #creacion del tweet como nodo y sus respectivas relaciones
    tx = m.begin()
    struct = []
    dest = []
    timet = time.strftime("%H:%M:%S")+","+time.strftime("%d/%m/%Y")
    struct.append(str(input("Que deseas publicar?\n")))
    while(int(input("Desea adicionar destinatarios? \n 1: si \n 2:no\n"))!=2):
        dest.append(str(input("A quienes deseas enviarselo:\n")))
        struct.append(dest)
    nuevotweet = Node("tweet",fecha=time.strftime("%H:%M:%S")+","+time.strftime("%d/%m/%Y"),texto=struct[0])
    tx.create(nuevotweet)
    tx.create(Relationship(node, "creatweet", nuevotweet))
    for x in dest:
        dic=m.run("MATCH (a:usuario) WHERE a.nombreu='"+x+"' RETURN a").evaluate()
        tx.create(Relationship(nuevotweet, "enviaa", dic))
    tx.commit()

def vertweetsRealizados(user, node): #retorna todos los tweets realizados por el usuario
    dic=m.run("MATCH (a)-[:creatweet]->(b) WHERE a.nombreu ='"+user.getusername()+"' RETURN b").data()
    if(dic is None):
        print("Aun no has realizado ningun tweet.\n")
        time.sleep(5)
        os.system('cls')
    else:
        for x in dic:
            for j in x.keys():
                print("tweet realizado: "+str(x[j]['texto'])+"\n"+"fecha en que se realizo: "+str(x[j]['fecha'])+"\n")
        if(int(input("Cerrar? \n 1:Si. \n"))):
            os.system('cls')
        else:
            os.system('cls')

def explorar(user, node): #muestra los tweets de las personas a las que un usuario sigue
    n = user.getfollowed()
    for x in n:
        dic=m.run("MATCH (a:usuario)-[:creatweet]->(t:tweet) WHERE a.nombreu = '"+x+"' RETURN t").data()
        dic=dic[0:4]
        if(len(dic)==0):
            print("Las personas a las que sigues aun no han publicado nada.\n")
            time.sleep(5)
            os.system('cls')
        else:
            for i in dic:
                for j in i.keys():
                    print("tweet: "+str(i[j]['texto'])+"\n"+"fecha en que se realizo: "+str(i[j]['fecha'])+"\n")
                if(int(input("Cerrar? \n 1: Si."))):
                    os.system('cls')
                    break
    

def cambiarmodo(user):
    """
Funcion que se encarga de cambiar los ajustes de privacidad del usuario(Privado ó Publico),
buscando su nodo y modificando su atributo de modou en alternancia al previo.
    """
    print("Actualmente tiene como modo asignado:"+str(user.getusermode())+"\n")
    if(int(input("Desea cambiarlo? 0:no 1:si\n"))):
        user.setusermode()
        m.run("MATCH (a:usuario) WHERE a.nombreu='"+user.getusername()+"' SET a.modou ='"+user.getusermode()+"'")#busqueda del usuario con nombre igual al proporcionado, al cual posteriormente se le hace cambio de propiedad con set
    os.system('cls')

def cambiarciudad(user,node):
    """
Funcion que tiene como parametros el un objeto usuario y su respectivo nodo, y permite mostrar
la ciudad registrada por el usuario, y da opcion de cambiarla, en caso de tener una previamente
asignada elimina la relacion entre estos dos; a la ciudad ingresada se le realiza una busqueda
de pre existencia para evitar redundancia de datos y en tal caso de no existencia se crea su nodo
y relaciona con el usuario, de otra forma solo los relaciona.
    """
    print("Actualmente tiene como ciudad asignada:"+str(user.getciudad())+"\n")
    if(int(input("Desea cambiarla? 0:no 1:si\n"))):
        ciudad=str(input("ingrese nombre de la ciudad de residencia con letra capital en mayuscula por favor."))
        if(not(user.getciudad() is None)):#verifica que la ciudad no sea Null
            m.run("MATCH (a:usuario)-[r:viveen]->(b:ciudad) WHERE a.nombreu='"+user.getusername()+"' and b.nombre='"+user.getciudad()+"' DELETE r")#si no lo es, borra la relacion preexistente
        tx=m.begin()#comienzo de inminente transaccion
        b=m.run("MATCH (a:ciudad) WHERE a.nombre='"+str(ciudad)+"' RETURN a").evaluate()#si existe se busca y retorna el nodo
        if(b is None):                                         #verifica existencia de un nodo con el nombre de esa ciudad en el grafo
            b=Node("ciudad",nombre=ciudad)                                                  #de no ser asi, se crea un nodo con su nombre
            tx.create(b)            
        ab = Relationship(node, "viveen", b)                                                #e independientemente se realiza una relacion entre usuario y ciudad
        tx.create(ab)
        tx.commit()                                                                         #se lleva a cabo la transaccion
        user.setciudad(ciudad)
    os.system('cls')
def buscar(nombre,node,user):
    dic=m.run("MATCH (a:usuario) WHERE a.nombreu='"+nombre+"' RETURN a").evaluate()
    o=3
    r=m.run("MATCH (b:usuario)-[r:follows {estado:['1']}]->(a:usuario) WHERE a.nombreu='"+nombre+"' and b.nombreu='"+node['nombreu']+"' RETURN r").evaluate()
    if(dic is None):
        print("Usuario inexistente.\n")
    else:
        tweets=m.run("MATCH (a:usuario)-[:creatweet]->(b:tweet) where a.nombreu='"+nombre+"' RETURN b").data()
        if(dic['modou']=="Privado" and (r is None)):
            print("este usuario es privado.\n")
            o=0
        elif(dic['modou']=="Privado" and (not(r is None))):
            o=3
            if(len(tweets) == 0):
                print("este usuario no ha realizado tweets hasta la fecha")
            else:
                for x in reversed(tweets):
                    for j in x.keys():
                        print(str(x[j]['fecha'])+"\n"+str(x[j]['texto'])+"\n-------------------------------------------------------------------")
        elif(dic['modou']=="Publico" and (r is None)):
            o=1
            if(len(tweets) == 0):
                print("este usuario no ha realizado tweets hasta la fecha")
            else:
                for x in reversed(tweets):
                    for j in x.keys():
                        print(str(x[j]['fecha'])+"\n"+str(x[j]['texto'])+"\n-------------------------------------------------------------------")
        elif(dic['modou']=="Publico" and (not(r is None))):
            o=3
            if(len(tweets) == 0):
                print("este usuario no ha realizado tweets hasta la fecha")
            else:
                for x in reversed(tweets):
                    for j in x.keys():
                        print(str(x[j]['fecha'])+"\n"+str(x[j]['texto'])+"\n-------------------------------------------------------------------")
        if(o!=3):
            if(int(input(("Desea mandar una solicitud de amistad? 0:no 1:si")))):
                tx=m.begin()
                ab = Relationship(node, "follows", dic)
                ab['estado']=[str(o)]
                tx.create(ab)
                tx.commit()
                if(o==1):
                    user.setnewfollowed(nombre)
    if(int(input("Cerrar? 1:si"))):
        os.system('cls')
def personasconocidas(user):
    dic=m.run("MATCH (a:usuario)-[:follows {estado:['1']}]->(b:usuario)-[:follows {estado:['1']}]->(c:usuario)-[:follows {estado:['1']}]->(d:usuario)-[:follows {estado:['1']}]->(e:usuario)-[:follows {estado:['1']}]->(f:usuario) WHERE a.nombreu='"+user.getusername()+"' RETURN f.nombreu AS nombre").data()
    while(True):
        for x in dic:
            print(str(x['nombre'])+"\n")
        if(int(input("Cerrar? 1:si\t0:no"))):
            os.system('cls')
            break
        else:os.system('cls')   
def iniciarsesion(user,nodou):
    global m
    o=1
    dic=m.run("MATCH (b:usuario)-[:follows {estado:['1']}]->(a:usuario) where a.nombreu='"+user.getusername()+"' RETURN b.nombreu AS Nombre").data()
    for x in dic:
        user.setnewfollower(x['Nombre'])
    dic=m.run("MATCH (a:usuario)-[:follows {estado:['1']}]->(b:usuario) where a.nombreu='"+user.getusername()+"' RETURN b.nombreu AS Nombre").data()
    for x in dic:
        user.setnewfollowed(x['Nombre'])
    dic=m.run("MATCH (b:usuario)-[:follows {estado:['0']}]->(a:usuario) where a.nombreu='"+user.getusername()+"' RETURN b.nombreu AS Nombre").data()
    for x in dic:
        user.setnewinvitation(x['Nombre'])
    user.setciudad(m.run("MATCH (a:usuario)-[:viveen]->(b:ciudad) WHERE a.nombreu='"+user.getusername()+"' RETURN b.nombre AS Nombre").evaluate())
    while o!=11:
        o=(int(input("Bienvenido "+user.getusername()+", que desea hacer\n 0:Ver mis seguidores\t\t\t 1:Ver usuarios seguidos\n 2:personas que quizas conozcas\t\t 3:Ver mis tweets realizados\n 4:Realizar tweet\t\t\t 5:Ver tweets recibidos\n 6:Explorar mis seguidos\t\t 7:Buscar usuario\n 8:Cambiar ajustes de privacidad \t 9:Cambiar o establecer ciudad\n 10:Ver soicitudes de amistad\t\t 11:Cerrar sesion\n")))
        if(o==0):
            mostrar_seguidores(user)
        elif(o==1):
            mostrar_seguidos(user)
        elif(o==2):
            personasconocidas(user)
        elif(o==3):
            vertweetsRealizados(user, nodou)
        elif(o==4):
            realizartweet(user, nodou)
        elif(o==5):
            vertweetsRecibidos(nodou, user)
        elif(o==6):
            explorar(user, nodou)
        elif(o==7):
            buscar(str(input("Ingrese cuenta de persona a buscar:")),nodou,user)
        elif(o==8):
            cambiarmodo(user)
        elif(o==9):
            cambiarciudad(user,nodou)
        elif(o==10):
            mostrar_invitaciones(user)
        elif(o==11):
            break
        else:
            continue
def main():
    global m
    print("Bienvenido, por favor ingrese sus datos de usuario\n")
    Paso=0
    while(not(Paso)):
        Nombre=str(input("Ingrese nombre de cuenta:\t"))
        Clave=str(input("Ingrese contraseña de cuenta:\t"))
        dic=m.run("MATCH (a:usuario) WHERE a.nombreu='"+Nombre+"' RETURN a").evaluate()#Devuelve el nodo al cual le pertenece un nombre igual al proporcionado por el usuario
        if(dic is None):
            print("Usuario inexistente")
            continue
        else:
            if(dic['passwordu']==Clave):#a este nodo se accede de manera igual a un diccionario, por lo tanto aqui obtenemos su clave y comparamos
                Paso=1
                User=usuario(Nombre,dic['modou'])
                os.system('cls')
                iniciarsesion(User,dic)
            else:
                print("Clave de ingreso incorrecto")
                continue
        os.system('cls')
main()
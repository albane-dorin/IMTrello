import projectClass

# Tests Column
c0 = projectClass.Column("Back-end")
c1 = projectClass.Column("Front-end")

print(c0.get_id())
print(c1.get_id())

print(c0.get_name())

c0.rename("Back-END")
print(c0.get_name())

# Tests Task

t1 = projectClass.Task("Classe Tâche", "création des fiches de tâches et leurs options", c0, None, 2024, 2, 20)

print(t1.get_status()) # /!\ renvoie le nombre

t1.rename("Class Task")
print(t1.get_name())

t1.new_description("programmation fiche tâche")
print(t1.get_description())

print(t1.get_column().get_id())
t1.move_column(c1)
print(t1.get_column().get_id())

t1.new_status(1)
print(t1.get_status())

print("Is it soon ?", t1.is_soon())
print("Is it late ?", t1.is_late())
t1.new_endDate(2024,1,22)
print("Is it soon ?", t1.is_soon())
print("Is it late ?", t1.is_late())
t1.new_endDate(2024,3,3)
print("Is it soon ?", t1.is_soon())
print("Is it late ?", t1.is_late())

#Tests Project

p = projectClass.Project("imtrello", "Test project", 2024,3,30,[c0, c1],
                         None, None)

p.rename("IMTrello")
print(p.get_name())

p.new_description("Création du Trello de l'IMT !")
print(p.get_description())

c2 = projectClass.Column("fonctions facultatives")
p.new_column(c2)
print(p.get_columns())

p.delete_column(c2)
print(p.get_columns())

t2 = projectClass.Task("Classe Project", "création de la classe projet", c1,
                       None, 2024, 2, 21)
p.new_task(t2)
print(p.get_tasks())

p.delete_task(t2)
print(p.get_tasks())
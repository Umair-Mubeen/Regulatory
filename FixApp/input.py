try:
    from models import Employee    
    name = input("Enter User Name : - ")
    pwd = input("Enter User Password : - ")
    email = input("Enter User Email : - ")
    age = input("Enter User Age : - ")
    dest = input("Enter User Destination : - ")
    add = input("Enter User Address : - ")
    emp = Employee(
        Emp_Name = name, 
        Emp_Pwd = pwd, 
        Emp_Email = email, 
        Emp_Age = age, 
        Emp_Designation = dest, 
        EmpAddress = add

        )
    emp.save()
except Exception as e:
    print(str(e))
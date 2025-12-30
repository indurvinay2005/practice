# temparature convertor:

unit = input("is this temp in celcius or fahrenheit (C/F): ")
temp = float(input("Enter the Temperature: "))

if unit == "C":
    temp = round((9* temp)/ 5 + 32, 1)
    print(f"The temp in fahrenheit is : {temp} F")
elif unit == "F":
    temp = round((temp - 32) * 5/9 ,1)
    print(f"The temp in celcius is : {temp} C")
else:
    print(f"{unit} is an invalid unit of measurement")
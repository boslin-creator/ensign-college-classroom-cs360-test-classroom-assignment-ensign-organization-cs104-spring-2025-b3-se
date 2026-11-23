import math  # Import the math module so we can use math.pi

radius = float(input("Enter the radius of the circle: "))  # Ask the user for the radius and convert it to a decimal number
diameter = 2 * radius  # Diameter is twice the radius (d = 2r)
circumference = 2 * math.pi * radius  # Circumference is 2 times pi times the radius (c = 2πr)
area = math.pi * radius ** 2  # Area is pi times the radius squared (A = πr²)

print(f"Diameter: {diameter}")  # Show the diameter to the user
print(f"Circumference: {circumference}")  # Show the circumference to the user
print(f"Area: {area}")  # Show the area to the user
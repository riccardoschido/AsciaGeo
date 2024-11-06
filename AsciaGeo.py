import numpy as np
import math as m
import matplotlib.pyplot as plt

def plt_profiles(coordinates):
	x_coord = []
	y_coord = []

	for i in range(len(coordinates)):
		x_coord.append(coordinates[i][0])
		y_coord.append(coordinates[i][1])

	plt.scatter(x_coord, y_coord)
	plt.axis('equal')
	plt.show()
def read_coordinates(input_file): # legge le coordinate dal file .txt
	coordinates = []
	with open(input_file, 'r') as coord_file:
		for points in coord_file:
			xy = points.strip().split()
			coordinates.append(xy)

	coordinates = [[float(x) for x in sottolista] for sottolista in coordinates]
	return coordinates
def translate_coordinates(coordinates, dx, dy): # trasla il profilo in base ad un input
	for i in range(len(coordinates)):
		coordinates[i][0] = coordinates[i][0] + dx
		coordinates[i][1] = coordinates[i][1] + dy

	return coordinates
def scale_profile(coordinates, C): # scala il profilo in base alla corda data in input
	for i in range(len(coordinates)):
		coordinates[i][0] = coordinates[i][0]*C
		coordinates[i][1] = coordinates[i][1]*C

	return coordinates
def rotate_coordinates(coordinates, AoA): # ruota le coordinate di un angolo che si dà in input
	alpha = AoA/180 *np.pi
	for i in range(len(coordinates)):
		coordinates[i][0] = coordinates[i][0]*m.cos(alpha) + coordinates[i][1]*m.sin(alpha)
		coordinates[i][1] = -coordinates[i][0]*m.sin(alpha) + coordinates[i][1]*m.cos(alpha)
	return coordinates
def define_data():
	n_profiles = int(input("Quanti profili ci sono? "))
	input_files = [0] * n_profiles
	AoA = [0] * n_profiles
	dx = [0] * n_profiles
	dy = [0] * n_profiles
	C = [0] * n_profiles

	for i in range(n_profiles):
		input_files[i] = input(f"Inserisci il percorso del file .txt delle coordinate del profilo {i + 1}: ")
		AoA[i] = float(input(f"inserisci l'angolo d'attacco del profilo {i + 1}: "))
		dx[i] = float(input(f"inserisci il deltaX del profilo {i + 1} (considera che il TE si trova nella posizione (0,1): "))
		dy[i] = float(input(f"inserisci il deltaY del profilo {i + 1} (considera che il TE si trova nella posizione (0,1): "))
		C[i] = float(input(f"inserisci corda profilo {i + 1}: "))

	H = float(input("inserisci dimensione farfield: "))
	lcc = float(input("inserisci risoluzione sui profili: "))
	lFF = float(input("inserisci risoluzione sul farfield: "))
	return n_profiles, input_files, AoA, dx, dy, C, H, lcc, lFF
def add_point_profile(coordinates, points_geo_file, lc):
	st = len(points_geo_file)
	n_points = len(coordinates)
	for i in range(n_points):
		points_geo_file.append(f"Point({i+st+1}) = {{{coordinates[i][0]}, {coordinates[i][1]}, 0, {lc}}};")
	return points_geo_file
def add_lines_profile(coordinates, lines_geo_file):
	st = len(lines_geo_file)
	n_points = len(coordinates)
	for i in range(1, n_points):
		lines_geo_file.append(f"Line({i+st}) = {{{i+st}, {i+st+1}}};")
	lines_geo_file.append(f"Line({n_points + st}) = {{{n_points+st}, {st+1}}};")
	return lines_geo_file
def add_loop_profile(loop_geo_file, lines_geo_file, coordinates):
	n_loops = len(loop_geo_file)
	n_lines = len(lines_geo_file)
	j = n_lines - len(coordinates)
	lines = ', '.join(str(i) for i in range(j+1, n_lines+1))
	loop_geo_file.append(f"Line Loop({n_loops+1}) = {{{lines}}};")
	return loop_geo_file
def add_farfield(H, lFF, points_geo_file, lines_geo_file, loop_geo_file):  # scrive dati riguardanti le geometrie del volume di controllo nel blocco delle coordinate
	n_points = len(points_geo_file)
	n_lines = len(lines_geo_file)
	n_loops = len(loop_geo_file)

	coordinates_farfield = []

	coordinates_farfield.append(f"Point({n_points + 1}) = {{0, 0, 0, {lFF}}};")
	coordinates_farfield.append(f"Point({n_points + 2}) = {{0, {H}, 0, {lFF} }};")
	coordinates_farfield.append(f"Point({n_points + 3}) = {{{H}, {H}, 0, {lFF} }};")
	coordinates_farfield.append(f"Point({n_points + 4}) = {{{H}, 0, 0, {lFF} }};")

	coordinates_farfield.append(f"Line({n_lines + 1}) = {{{n_lines + 1}, {n_lines + 2}}};")
	coordinates_farfield.append(f"Line({n_lines + 2}) = {{{n_lines + 2}, {n_lines + 3}}};")
	coordinates_farfield.append(f"Line({n_lines + 3}) = {{{n_lines + 3}, {n_lines + 4}}};")
	coordinates_farfield.append(f"Line({n_lines + 4}) = {{{n_lines + 4}, {n_lines + 1}}};")

	coordinates_farfield.append(f"Line Loop({n_loops + 1}) = {{{n_lines + 1}, {n_lines + 2}, {n_lines + 3}, {n_lines + 4}}};")

	plane_surface = ', '.join(str(i) for i in range(n_loops+1, 0, -1))

	coordinates_farfield.append(f"Plane Surface(1) = {{{plane_surface}}};")

	return coordinates_farfield
def write_geo_file(geo_content):
	with open("mesh.geo", "w") as file:
		file.write("\n".join(geo_content))

if __name__ ==  "__main__": 
	print("#####################################################################")
	print("#                         Welcome in AsciaGeo                       #")
	print("#  Questo è un tool che permette di creare facilmente un file .geo  #")
	print("#            AsciaGeo è stato sviluppato da Asciaibo ed è           #")
	print("#	         diffuso gratuitamente in nome dell'OpenSource     #")
	print("#####################################################################")

	n_profiles, input_files, AoA, dx, dy, C, H, lcc, lFF = define_data()

	coords_tot = []
	points_geo = []
	lines_geo = []
	loop_geo = []


	for i in range(n_profiles):
		coords = read_coordinates(input_files[i])
		scale_profile(coords, C[i])
		rotate_coordinates(coords, AoA[i])
		translate_coordinates(coords, dx[i], dy[i])

		add_point_profile(coords, points_geo, lcc)
		add_lines_profile(coords, lines_geo)
		add_loop_profile(loop_geo, lines_geo, coords)
		coords_tot = coords_tot + coords

	plt_profiles(coords_tot)

	farfield_geo = add_farfield(H, lFF, points_geo, lines_geo, loop_geo)

	geo_content = points_geo + lines_geo + loop_geo + farfield_geo

	write_geo_file(geo_content)

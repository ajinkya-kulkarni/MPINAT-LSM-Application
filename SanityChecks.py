
# Function which ...

def SanityChecks(my_list1, my_list2, my_list3):

	counter = 0

	for i in range(len(my_list1)):

		if my_list1[i] == 'Yes':

			if (float(my_list2[i]) < 0 or my_list2[i] == '0' or float(my_list3[i]) < 0 or my_list3[i] == '0'):
				
				counter = counter + 1

		else:
			
			if (float(my_list2[i]) < 0 or my_list2[i] != '0' or float(my_list3[i]) < 0 or my_list3[i] != '0'):
				
				counter = counter + 1

	return counter
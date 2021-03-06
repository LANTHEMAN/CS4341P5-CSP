#!/usr/bin/python
import Bag
import Items
import sys
import InputReader


# check upper bag limit, return true if pass
def check_upper_bag_limit(parameter, bag_index):
    if len(parameter.list_of_bags[bag_index].contains) + 1 <= parameter.upper_limit:
        return True
    else:
        return False


# check unary inclusive, return true if pass
def check_unary_inclusive(next_item, parameter, bag_index):
    if next_item in parameter.unary_inclusive:
        if parameter.list_of_bags[bag_index] in parameter.unary_inclusive[next_item]:
            return True
        else:
            #print("The bag you tried to add is not in unary inclusive list")
            return False
    else:
        return True


# check unary exclusive, return true if pass
def check_unary_exclusive(next_item, parameter, bag_index):
    if next_item in parameter.unary_exclusive:
        if parameter.list_of_bags[bag_index] not in parameter.unary_exclusive[next_item]:
            return True
        else:
            #print("The bag you tried to add is in unary exclusive list")
            return False
    return True


# check binary equal, return true if pass
def check_binary_equal(next_item,parameter,bag_index):
    for i in parameter.binary_equal:
        if next_item in i:
            for j in i:
                if not j == next_item:
                    if j in parameter.list_of_items:
                        return True
                    elif j.bag == parameter.list_of_bags[bag_index]:
                        return True
                    else:
                        return False

    return True


# check binary not equal, return true if pass
def check_binary_not_equal(next_item,parameter,bag_index):
    for i in parameter.binary_not_equal:
        if next_item in i:
            for j in i:
                if not j == next_item:
                    if j in parameter.list_of_items:
                        return True
                    elif not j.bag == parameter.list_of_bags[bag_index]:
                        return True
                    else:
                        return False
    return True


# check mutual inclusive, return true if pass
def check_mutual_inclusive(next_item,parameter,bag_index):
    for mi in parameter.mutual_inclusive:
        # check if in item list
        if next_item in mi[0]:
            # loop through the item tuple in a single constraint
            for i in mi[0]:
                # get the value already assigned (not the current item)
                if i.bag and (i.bag in mi[1]):
                    for b in mi[1]:
                        if not b == i.bag:
                            if not parameter.list_of_bags[bag_index] == b:
                                # print('next_item: ',next_item.name,' bag[i]: ',parameter.list_of_bags[bag_index].name)
                                # print('false',mi[0][0].name,mi[0][1].name,mi[1][0].name,mi[1][1].name,'\n')
                                return False

                if i == next_item and (parameter.list_of_bags[bag_index] in mi[1]):
                    for d in mi[0]:
                        if (not d == next_item) and d.bag:
                            current_item = d
                            for c in mi[1]:
                                if not c == parameter.list_of_bags[bag_index]:
                                    if not current_item.bag == c:
                                        return False

    return True


# check if all constraints pass
def valid_assignment(next_item,parameter,bag_index):
    if(
            check_upper_bag_limit(parameter, bag_index) and
            check_unary_inclusive(next_item,parameter,bag_index) and
            check_unary_exclusive(next_item, parameter, bag_index) and
            check_binary_equal(next_item, parameter, bag_index) and
            check_binary_not_equal(next_item, parameter, bag_index) and
            check_mutual_inclusive(next_item, parameter, bag_index)):
        return True
    else:
        return False


# select next item in list
def select_unassigned_variable(parameter):
    return parameter.list_of_items.pop(0)


# back track
def back_tracking(parameter):
    if finished(parameter):
        return True

    if parameter.list_of_items:
        next_item = select_unassigned_variable(parameter)
    else:
        return False
    #sort bag by minimum remaining value
    copy_of_bag_list = parameter.list_of_bags.copy()
    sort_bag_by_minimum_remaining_value(copy_of_bag_list)

    for g in range(len(parameter.list_of_bags)):
        # find the according index in original list of bags
        i = 0
        for t in range(len(parameter.list_of_bags)):
            if parameter.list_of_bags[t].name == copy_of_bag_list[g].name:
                i = t

        if valid_assignment(next_item, parameter,i):
            ######################################
            # forward checking of if the bag can fit the item in it
            ######################################
            added = parameter.list_of_bags[i].add_item(next_item)
            if added:
                outcome = back_tracking(parameter)
                if outcome:
                    return True
                else:
                    parameter.list_of_bags[i].remove_item(next_item)
    parameter.list_of_items.append(next_item)
    return False


# sort key of remaining cap
def remaining_capacity(bag):
    remaining_cap = bag.capacity - bag.current_load
    return remaining_cap


######################################
# minimum_remaining_value
######################################
def sort_bag_by_minimum_remaining_value(list_of_bags):
    list_of_bags.sort(reverse=True, key=remaining_capacity)


# sort key of num_of_constraints
def item_num_of_constraints(item):
    return item.num_of_constraints


######################################
# least_constraint_value
######################################
def sort_item_by_least_constraint_value(parameter):
    for item in parameter.list_of_items:
        constraint_counter = 0
        if item in parameter.unary_inclusive:
            constraint_counter += 1
        if item in parameter.unary_exclusive:
            constraint_counter += 1
        for a in parameter.binary_equal:
            if item in a:
                constraint_counter += 1
        for b in parameter.binary_not_equal:
            if item in b:
                constraint_counter += 1
        for c in parameter.mutual_inclusive:
            if item in c[0]:
                constraint_counter += 1
        item.num_of_constraints = constraint_counter
    parameter.list_of_items.sort(key=item_num_of_constraints)


# check finishing condition
def finished(parameter):
    for a in parameter.list_of_bags:
        if (a.capacity - a.current_load) > 1:
            return False
    if len(parameter.list_of_items) == 0:
        return True
    else:
        return False


if __name__ == "__main__":
    param = InputReader.Input(sys.argv[1])
    param.InterpretFile()
    sort_item_by_least_constraint_value(param)

    result = back_tracking(param)
    out_file = open(sys.argv[2],'w')

    if result:
        for a in param.list_of_bags:
            line = [a.name+' ']
            for b in a.contains:
                line.append(b.name)
                line.append(' ')
            out_file.write(''.join(line))
            out_file.write('\n')
            num_of_items = 'number of items: ' + str(len(a.contains)) + '\n'
            out_file.write(num_of_items)
            total_weight_capacity = 'total weight: '+str(a.current_load)+' '+'total capacity: '+str(a.capacity)+'\n'
            out_file.write(total_weight_capacity)
            wasted = 'wasted capacity: ' + str(a.capacity - a.current_load)+'\n'
            out_file.write(wasted)
            out_file.write('\n')
    else:
        out_file.write('No solution found')

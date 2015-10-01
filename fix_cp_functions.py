from api.models.ComponentPoint import ComponentPoint
from db.uow import UoW
from function_parser import FunctionParser
from function_parser.tokenizer import InvalidTokenException

__author__ = 'Brian'


class CPFixer:
    def __init__(self, uow=None):
        if not uow:
            self.uow = UoW(False)
        else:
            self.uow = uow

    @staticmethod
    def previous_value_is_alpha(formula, position):
        return formula[position - 1] in ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j",
                                         "k", "l", "m", "n", "o", "p", "q", "r", "s", "t",
                                         "u", "v", "w", "x", "y", "z",
                                         "A", "B", "C", "D", "E", "F", "G", "H", "I", "J",
                                         "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
                                         "U", "V", "W", "X", "Y", "Z"]

    @staticmethod
    def previous_value_is_number(formula, position):
        return formula[position - 1] in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

    def fix_zeros_for_point(self, point, position):
        """
        Make sure there is a token before the decimal, and if there is, or if it is the first thing, then add a 0 before
        the decimal
        """

        if position == 0:
            # add 0 in front of decimal to make sure it works right
            point['formula'] = '0' + point['formula']
        else:
            # check to make sure the error is caused by a decimal without a leading number and if it is, update it
            if not self.previous_value_is_alpha(point['formula'], position) and not self.previous_value_is_number(point['formula'], position):
                point['formula'] = point['formula'][0:position] + '0' + point['formula'][position:]
            else:
                print point['id']
                return

        # make a point object
        point_obj = ComponentPoint(point)

        # update the point
        self.uow.component_points.update(point_obj)

        # check to make sure the function is working properly
        self.handle_zeros_for_point(point)

    def handle_zeros_for_point(self, point):
        """
        Checks if the function can be parsed, and if it can't, it sends the point to be fixed
        """
        try:
            FunctionParser.parse(point['formula'])
        except InvalidTokenException as e:
            # function cannot be parsed
            self.fix_zeros_for_point(point, e.position)

    def fix_leading_zeros(self):
        """
        Finds all of the functions that are missing a leading 0 for a decimal. If it is missing one, add it. Otherwise ignore
        """
        points = self.uow.component_points.get_all_cp_with_decimal()
        for point in points:
            self.handle_zeros_for_point(point)

    @staticmethod
    def check_if_parameters_are_valid(parameters, identifier_names):
        """
        Checks the length of the parameters with the identifiers in the expression tree
        """
        param_names = set([x['name'].lower() for x in parameters])
        set_id_names = set([y.lower() for y in identifier_names if y != "IF" and y != "ABS" and y != "POWER"])
        return param_names == set_id_names

    def match_parameter_names(self, point, identifier_names):
        """
        Matches the points parameters based on the identifier names, with the other points included in the component
        """
        component_points = self.uow.component_points.get_points_for_component_id(point['component_id'])

        # create a dictionary of the component points for the given component based on lowercase code
        component_points_by_name = dict([(x['code'].lower(), x) for x in component_points])

        parameter_list = []
        for name in identifier_names:
            # find the correct component point by name
            try:
                new_param = {'name': name.upper(),
                             'point_id': component_points_by_name[name.lower()]['id']}
                parameter_list.append(new_param)
            except:
                continue

        point['parameters'] = parameter_list
        if not self.check_if_parameters_are_valid(point['parameters'], identifier_names):
            print point['id']
        # update the point with the new parameter list
        point_obj = ComponentPoint(point)
        self.uow.component_points.update(point_obj)

    def fix_parameters_for_point(self, point, identifier_names):
        """
        Checks if all of the parameters exist already, and if not it creates them based on name
        """
        parameters_valid = self.check_if_parameters_are_valid(point['parameters'], identifier_names)
        if not parameters_valid:
            # match up the parameters on the point with the associated points on the same component
            self.match_parameter_names(point, identifier_names)

    def handle_parameters_for_point(self, point):
        """
        If the equation is valid, it will pass the point and the expression tree to get fixed
        """
        try:
            expression_tree = FunctionParser.parse(point['formula'])
            if len(expression_tree['identifier_names']) > 0:
                self.fix_parameters_for_point(point, expression_tree['identifier_names'])
        except:
            print point['id']

    def fix_parameters(self):
        """
        Sends all of the component points to get their parameter references fixed
        """
        points = self.uow.component_points.get_points_by_type("CP")
        for point in points:
            if not 'parameters' in point:
                point['parameters'] = []
            self.handle_parameters_for_point(point)

    def run(self):
        """
        Fix the issues with the calculated points that were imported.
            1. There are decimals without a leading number. Find all of these and update them to have a leading 0
            2. The names are there for the variables, however, they aren't matched to a point. We will map these to the
                proper points, and log all of the formulas where that can't be done, to be manually fixed later
        """
        print "Fixing leading zeros..."
        self.fix_leading_zeros()
        print "Fixing parameters..."
        self.fix_parameters()


if __name__ == "__main__":
    fixer = CPFixer()
    fixer.run()
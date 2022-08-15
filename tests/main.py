from pysimlink import Model, print_all_params
import argparse
import numpy as np



def main(args):
    model = Model(args.model_name, args.model_path)#, force_rebuild=True)
    model.reset()

    param = model.get_model_param(model_name='HevP4ReferenceApplication/Passenger Car/Drivetrain/Drivetrain', param='G')
    print(param)
    G = np.full((1,7), 5)
    model.set_model_param(model_name='HevP4ReferenceApplication/Passenger Car/Drivetrain/Drivetrain', param='G', value=G)
    param = model.get_model_param(model_name='HevP4ReferenceApplication/Passenger Car/Drivetrain/Drivetrain', param='G')
    print(param)

    # print_all_params(model)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("model_name")
    parser.add_argument("model_path")
    args = parser.parse_args()
    main(args)

import pandas as pd


class MakeCSV:
    def __init__(self, data: list):
        self.data = data

    def dict_list_to_data_frame(self):
        print(self.data)
        res = pd.DataFrame(
            columns=["x", "y", "z"],
        )
        for point_dict in self.data:
            pd.concat(
                [
                    res,
                    pd.DataFrame(
                        {
                            "x": point_dict["coords"].x,
                            "y": point_dict["coords"].y,
                            "z": point_dict["coords"].z,
                        }
                    ),
                ]
            )
        print(res)

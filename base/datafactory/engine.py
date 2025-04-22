import json
import time
import sys

import pandas as pd
from statsmodels.tsa.api import ExponentialSmoothing

read_path = 'base/datafactory/data/raw/api_response.json'

with open(read_path, 'r') as f:
    data = json.load(f)

# get current hour
current_hour = int(time.strftime("%H", time.localtime()))

while current_hour > 9:
    extracted = []
    for record in data:
        for match in record:
            match_id = match['match_id']
            match_status = match.get('match_status', 'no status')
            match_hometeam_score = match.get('match_hometeam_score', 'no score')
            match_awayteam_score = match.get('match_awayteam_score', 'no score')

            stats = match['statistics']
            home_attacks = [stat['home'] for stat in stats if stat['type'] == 'Attacks'][0]

            response_dict = {
                'match_id': match_id,
                'match_status': match_status,
                'match_hometeam_score': match_hometeam_score,
                'match_awayteam_score': match_awayteam_score,
                'home_attacks': home_attacks
            }
            extracted.append(response_dict)
            df = pd.DataFrame(extracted)
            df = df.astype("int64")
            df = df.groupby("match_status").max().reset_index()

            if len(df) > 5:
                # exponential smoothing fit:
                model = (ExponentialSmoothing(df['home_attacks'],
                                            trend='add',
                                            seasonal='add',
                                            seasonal_periods=2)
                                            ).fit()
                # predict next 1 value:
                forecast_array = model.forecast(1)
                goal_pred = ['True' if forecast_array.values[0] > df['home_attacks'].values[-5]*1.07 else 'False' for i in forecast_array]
                #find the last index of the df:
                last_index = df.index[-1]
                # add the forescast and goal_pred to the df:
                df.loc[last_index, 'forecast'] = forecast_array.values[0]
                df.loc[last_index, 'goal_pred'] = goal_pred[0]

                #pred_df = pd.DataFrame(list(zip(forecast_array, goal_pred)), columns=['forecast', 'goal_pred'])
                #df = pd.concat([df, pred_df], axis=0)

                #max_match_status = int(df['match_status'].max())
                #status_range = range(max_match_status+1, max_match_status + 6)
                # print(status_range)
                #df.loc[:, 'match_status'].iloc[-5:] = status_range
                
            else:
                df.loc[:, 'forecast'] = None
                df.loc[:, 'goal_pred'] = 'False'

            write_path = 'base/datafactory/data/output/extracted.csv'
            write_path_json = 'base/datafactory/data/output/extracted.json'
            #with open(write_path_json, 'w') as f:
            #    json.dump(df.to_dict('records'), f, indent=4)
            df.tail(1).to_json(write_path_json, orient='records', indent=4)
                
            df.tail(1).to_csv(write_path, index=False)
            time.sleep(2)


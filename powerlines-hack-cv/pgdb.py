import psycopg2
from datetime import datetime, timedelta


class PostgreSqlDatabase:

    def __init__(self, config):
        self.connection_string = config["database_url"]
        self.connection = self.get_connection()

    def get_connection(self):
        pg_conn = psycopg2.connect(self.connection_string)
        pg_conn.autocommit = False
        return pg_conn

    def write_cv_result(self, result):
        task_id = result['task_id']
        result_link = result['result_link']
        line_broken = result['line_broken']
        vibration_damper_displacement = result['vibration_damper_displacement']
        garland_problem = result['garland_problem']

        pg_cursor = self.connection.cursor()
        insert_processing_result = """
            UPDATE tasks
            SET result_link=%s, line_broken=%s, vibration_damper_displacement=%s, garland_problem=%s
            WHERE id=%s
        """
        pg_cursor.execute(insert_processing_result,
                          (
                           result_link,
                           line_broken,
                           vibration_damper_displacement,
                           garland_problem,
                           task_id
                           )
        )
        pg_cursor.close()

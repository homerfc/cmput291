import cx_Oracle

class Oracle(object):

    def connect(self, username, password, hostname, port, servicename):
        """ Connect to the database. """

        try:
            self.db = cx_Oracle.connect(username, password
                                , hostname + ':' + port + '/' + servicename)
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            if error.code == 1017:
                print('Please check your credentials.')
            else:
                print('Database connection error: %s'.format(e))
            # Very important part!
            raise

        # If the database connection succeeded create the cursor
        # we-re going to use.
        self.cursor = self.db.cursor()

    def disconnect(self):
        """
        Disconnect from the database. If this fails, for instance
        if the connection instance doesn't exist we don't really care.
        """

        try:
            self.cursor.close()
            self.db.close()
        except cx_Oracle.DatabaseError:
            pass

    def execute(self, sql, bindvars=None, commit=False):
        """
        Execute whatever SQL statements are passed to the method;
        commit if specified. Do not specify fetchall() in here as
        the SQL statement may not be a select.
        bindvars is a dictionary of variables you pass to execute.
        """

        try:
            self.cursor.execute(sql, bindvars)
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            if error.code == 955:
                print('Table already exists')
            elif error.code == 1031:
                print("Insufficient privileges")
            print(error.code)
            print(error.message)
            print(error.context)

            # Raise the exception.
            raise

        # Only commit if it-s necessary.
        if commit:
            self.db.commit()


if __name__ == "__main__":
  
                  try:
                      oracle = Oracle.connect('username', 'password', 'hostname'
                                             , 'port', 'servicename')

                      # No commit as you don-t need to commit DDL.
                      oracle.execute('ddl_statements')

                  # Ensure that we always disconnect from the database to avoid
                  # ORA-00018: Maximum number of sessions exceeded.
                  finally:
                      oracle.disconnect()

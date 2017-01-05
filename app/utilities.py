class DB_util():
    """
    Relational DB Utilities
    """
    def __init__(self, db):
        self.db = db # connect to db
        self.tmp_session = []

    def drop(self):
        """
        For current version of sql-alchemy, have two issues with Postgres: 
        Postgres Lock When call drop_all, and also does not drop in cascade order.
        This function is a workaround.

        Credit http://www.sqlalchemy.org/trac/wiki/UsageRecipes/DropEverything
        """
        print '-- UTIL::DATABASE::DROP START --'
        from sqlalchemy.engine import reflection
        from sqlalchemy.schema import (
            MetaData,
            Table,
            DropTable,
            ForeignKeyConstraint,
            DropConstraint,
        )
        conn=self.db.engine.connect()
        trans = conn.begin()
        inspector = reflection.Inspector.from_engine(self.db.engine)
        metadata = MetaData()
        tbs = []
        all_fks = []
        for table_name in inspector.get_table_names():
            fks = []
            for fk in inspector.get_foreign_keys(table_name):
                if not fk['name']:
                    continue
                fks.append(
                    ForeignKeyConstraint((),(),name=fk['name'])
                )
            t = Table(table_name,metadata,*fks)
            tbs.append(t)
            all_fks.extend(fks)

        for fkc in all_fks:
            conn.execute(DropConstraint(fkc))
        for table in tbs:
            conn.execute(DropTable(table))
        trans.commit()
        print ' -- UTIL::DATABASE::DROP END --'

    def create(self):
        print "-- UTIL::DATABASE::CREATE START --"
        self.db.create_all()
        print "-- UTIL::DATABASE::CREATE END --"

    def reset(self):
        print '-- UTIL::DATABASE::RESET START --'
        self.drop()
        self.create()
        print '-- UTIL::DATABASE::RESET END --'

    # -- Session Control --
    def add(self, db_obj):
        """
        add and commit the data
        """
        self.db.session.add(db_obj)
        self.db.session.commit()

    def delete(self, db_obj):
        self.db.session.delete(db_obj)
        self.db.session.commit()

    def commit(self):
        self.db.session.commit()
    
    def get(self, column, name):
        """
        Get one row from column
        """
        self.db.session.query(column).get(name)

    def get_column(self, column):
        """
        Get all data from column.
        """
        self.db.session.query(column).all()

class Preload():
    """
    Preload some basic data after refresh database.
    """
    def __init__(self, db_util, db_schema, fire_schema):
        self.db = db_schema
        self.fire = fire_schema
        self.db_util = db_util

    def reset_db(self, relational=False, realtime=False):
        """
        Reset DBs then preload data
        """
        # ---- relational db reset ----
        if relational:
            self.db._RESET_DB()

        # ---- firedb reset ----
        if realtime:
            self.fire._RESET_DB()

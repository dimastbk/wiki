import os

from flask_sqlalchemy import SQLAlchemy as FlaskSQLAlchemy
from flask_sqlalchemy import _sa_url_query_setdefault, _sa_url_set
from sqlalchemy.pool import NullPool


class SQLAlchemy(FlaskSQLAlchemy):
    def apply_driver_hacks(self, app, sa_url, options):
        if sa_url.drivername.startswith("mysql"):
            sa_url = _sa_url_query_setdefault(sa_url, charset="utf8")

            if sa_url.drivername != "mysql+gaerdbms" and isinstance(
                options.get("poolclass"), NullPool
            ):
                options.setdefault("pool_size", 10)
                options.setdefault("pool_recycle", 7200)
        elif sa_url.drivername == "sqlite":
            pool_size = options.get("pool_size")
            detected_in_memory = False
            if sa_url.database in (None, "", ":memory:"):
                detected_in_memory = True
                from sqlalchemy.pool import StaticPool

                options["poolclass"] = StaticPool
                if "connect_args" not in options:
                    options["connect_args"] = {}
                options["connect_args"]["check_same_thread"] = False

                # we go to memory and the pool size was explicitly set
                # to 0 which is fail.  Let the user know that
                if pool_size == 0:
                    raise RuntimeError(
                        "SQLite in memory database with an "
                        "empty queue not possible due to data "
                        "loss."
                    )
            # if pool size is None or explicitly set to 0 we assume the
            # user did not want a queue for this sqlite connection and
            # hook in the null pool.
            elif not pool_size:
                options["poolclass"] = NullPool

            # if it's not an in memory database we make the path absolute.
            if not detected_in_memory:
                sa_url = _sa_url_set(
                    sa_url, database=os.path.join(app.root_path, sa_url.database)
                )

        unu = app.config["SQLALCHEMY_NATIVE_UNICODE"]
        if unu is None:
            unu = self.use_native_unicode
        if not unu:
            options["use_native_unicode"] = False

        return sa_url, options

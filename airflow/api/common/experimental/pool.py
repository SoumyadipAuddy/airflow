#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""Pool APIs."""
from __future__ import annotations

from deprecated import deprecated
from sqlalchemy import select
from sqlalchemy.orm import Session

from airflow.exceptions import AirflowBadRequest, PoolNotFound
from airflow.models import Pool
from airflow.utils.session import NEW_SESSION, provide_session


@deprecated(reason="Use Pool.get_pool() instead", version="2.2.4")
@provide_session
def get_pool(name, session: Session = NEW_SESSION):
    """Get pool by a given name."""
    if not (name and name.strip()):
        raise AirflowBadRequest("Pool name shouldn't be empty")

    pool = session.scalar(select(Pool).filter_by(pool=name).limit(1))
    if pool is None:
        raise PoolNotFound(f"Pool '{name}' doesn't exist")

    return pool


@deprecated(reason="Use Pool.get_pools() instead", version="2.2.4")
@provide_session
def get_pools(session: Session = NEW_SESSION):
    """Get all pools."""
    return session.scalars(select(Pool)).all()


@deprecated(reason="Use Pool.create_pool() instead", version="2.2.4")
@provide_session
def create_pool(name, slots, description, session: Session = NEW_SESSION):
    """Create a pool with given parameters."""
    if not (name and name.strip()):
        raise AirflowBadRequest("Pool name shouldn't be empty")

    try:
        slots = int(slots)
    except ValueError:
        raise AirflowBadRequest(f"Bad value for `slots`: {slots}")

    # Get the length of the pool column
    pool_name_length = Pool.pool.property.columns[0].type.length
    if len(name) > pool_name_length:
        raise AirflowBadRequest(f"Pool name can't be more than {pool_name_length} characters")

    session.expire_on_commit = False
    pool = session.scalar(select(Pool).filter_by(pool=name).limit(1))
    if pool is None:
        pool = Pool(pool=name, slots=slots, description=description, include_deferred=False)
        session.add(pool)
    else:
        pool.slots = slots
        pool.description = description

    session.commit()

    return pool


@deprecated(reason="Use Pool.delete_pool() instead", version="2.2.4")
@provide_session
def delete_pool(name, session: Session = NEW_SESSION):
    """Delete pool by a given name."""
    if not (name and name.strip()):
        raise AirflowBadRequest("Pool name shouldn't be empty")

    if name == Pool.DEFAULT_POOL_NAME:
        raise AirflowBadRequest(f"{Pool.DEFAULT_POOL_NAME} cannot be deleted")

    pool = session.scalar(select(Pool).filter_by(pool=name).limit(1))
    if pool is None:
        raise PoolNotFound(f"Pool '{name}' doesn't exist")

    session.delete(pool)
    session.commit()

    return pool

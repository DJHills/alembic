import sys
from alembic.testing import TestBase, config, mock

from sqlalchemy import MetaData, Column, Table, Integer, String, \
    ForeignKeyConstraint
from alembic.testing import eq_

py3k = sys.version_info.major >= 3

from ._autogen_fixtures import AutogenFixtureTest


class AutogenerateForeignKeysTest(AutogenFixtureTest, TestBase):
    __backend__ = True

    def test_remove_fk(self):
        m1 = MetaData()
        m2 = MetaData()

        Table('some_table', m1,
              Column('test', String(10), primary_key=True),
              mysql_engine='InnoDB')

        Table('user', m1,
              Column('id', Integer, primary_key=True),
              Column('name', String(50), nullable=False),
              Column('a1', String(10), server_default="x"),
              Column('test2', String(10)),
              ForeignKeyConstraint(['test2'], ['some_table.test']),
              mysql_engine='InnoDB')

        Table('some_table', m2,
              Column('test', String(10), primary_key=True),
              mysql_engine='InnoDB')

        Table('user', m2,
              Column('id', Integer, primary_key=True),
              Column('name', String(50), nullable=False),
              Column('a1', String(10), server_default="x"),
              Column('test2', String(10)),
              mysql_engine='InnoDB'
              )

        diffs = self._fixture(m1, m2)

        self._assert_fk_diff(
            diffs[0], "remove_fk",
            "user", ['test2'],
            'some_table', ['test'],
            conditional_name="servergenerated"
        )

    def test_add_fk(self):
        m1 = MetaData()
        m2 = MetaData()

        Table('some_table', m1,
              Column('id', Integer, primary_key=True),
              Column('test', String(10)),
              mysql_engine='InnoDB')

        Table('user', m1,
              Column('id', Integer, primary_key=True),
              Column('name', String(50), nullable=False),
              Column('a1', String(10), server_default="x"),
              Column('test2', String(10)),
              mysql_engine='InnoDB')

        Table('some_table', m2,
              Column('id', Integer, primary_key=True),
              Column('test', String(10)),
              mysql_engine='InnoDB')

        Table('user', m2,
              Column('id', Integer, primary_key=True),
              Column('name', String(50), nullable=False),
              Column('a1', String(10), server_default="x"),
              Column('test2', String(10)),
              ForeignKeyConstraint(['test2'], ['some_table.test']),
              mysql_engine='InnoDB')

        diffs = self._fixture(m1, m2)

        self._assert_fk_diff(
            diffs[0], "add_fk",
            "user", ["test2"],
            "some_table", ["test"]
        )

    def test_no_change(self):
        m1 = MetaData()
        m2 = MetaData()

        Table('some_table', m1,
              Column('id', Integer, primary_key=True),
              Column('test', String(10)),
              mysql_engine='InnoDB')

        Table('user', m1,
              Column('id', Integer, primary_key=True),
              Column('name', String(50), nullable=False),
              Column('a1', String(10), server_default="x"),
              Column('test2', Integer),
              ForeignKeyConstraint(['test2'], ['some_table.id']),
              mysql_engine='InnoDB')

        Table('some_table', m2,
              Column('id', Integer, primary_key=True),
              Column('test', String(10)),
              mysql_engine='InnoDB')

        Table('user', m2,
              Column('id', Integer, primary_key=True),
              Column('name', String(50), nullable=False),
              Column('a1', String(10), server_default="x"),
              Column('test2', Integer),
              ForeignKeyConstraint(['test2'], ['some_table.id']),
              mysql_engine='InnoDB')

        diffs = self._fixture(m1, m2)

        eq_(diffs, [])

    def test_no_change_composite_fk(self):
        m1 = MetaData()
        m2 = MetaData()

        Table('some_table', m1,
              Column('id_1', String(10), primary_key=True),
              Column('id_2', String(10), primary_key=True),
              mysql_engine='InnoDB')

        Table('user', m1,
              Column('id', Integer, primary_key=True),
              Column('name', String(50), nullable=False),
              Column('a1', String(10), server_default="x"),
              Column('other_id_1', String(10)),
              Column('other_id_2', String(10)),
              ForeignKeyConstraint(['other_id_1', 'other_id_2'],
                                   ['some_table.id_1', 'some_table.id_2']),
              mysql_engine='InnoDB')

        Table('some_table', m2,
              Column('id_1', String(10), primary_key=True),
              Column('id_2', String(10), primary_key=True),
              mysql_engine='InnoDB'
              )

        Table('user', m2,
              Column('id', Integer, primary_key=True),
              Column('name', String(50), nullable=False),
              Column('a1', String(10), server_default="x"),
              Column('other_id_1', String(10)),
              Column('other_id_2', String(10)),
              ForeignKeyConstraint(['other_id_1', 'other_id_2'],
                                   ['some_table.id_1', 'some_table.id_2']),
              mysql_engine='InnoDB')

        diffs = self._fixture(m1, m2)

        eq_(diffs, [])

    def test_add_composite_fk_with_name(self):
        m1 = MetaData()
        m2 = MetaData()

        Table('some_table', m1,
              Column('id_1', String(10), primary_key=True),
              Column('id_2', String(10), primary_key=True),
              mysql_engine='InnoDB')

        Table('user', m1,
              Column('id', Integer, primary_key=True),
              Column('name', String(50), nullable=False),
              Column('a1', String(10), server_default="x"),
              Column('other_id_1', String(10)),
              Column('other_id_2', String(10)),
              mysql_engine='InnoDB')

        Table('some_table', m2,
              Column('id_1', String(10), primary_key=True),
              Column('id_2', String(10), primary_key=True),
              mysql_engine='InnoDB')

        Table('user', m2,
              Column('id', Integer, primary_key=True),
              Column('name', String(50), nullable=False),
              Column('a1', String(10), server_default="x"),
              Column('other_id_1', String(10)),
              Column('other_id_2', String(10)),
              ForeignKeyConstraint(['other_id_1', 'other_id_2'],
                                   ['some_table.id_1', 'some_table.id_2'],
                                   name='fk_test_name'),
              mysql_engine='InnoDB')

        diffs = self._fixture(m1, m2)

        self._assert_fk_diff(
            diffs[0], "add_fk",
            "user", ['other_id_1', 'other_id_2'],
            'some_table', ['id_1', 'id_2'],
            name="fk_test_name"
        )

    @config.requirements.no_name_normalize
    def test_remove_composite_fk(self):
        m1 = MetaData()
        m2 = MetaData()

        Table('some_table', m1,
              Column('id_1', String(10), primary_key=True),
              Column('id_2', String(10), primary_key=True),
              mysql_engine='InnoDB')

        Table('user', m1,
              Column('id', Integer, primary_key=True),
              Column('name', String(50), nullable=False),
              Column('a1', String(10), server_default="x"),
              Column('other_id_1', String(10)),
              Column('other_id_2', String(10)),
              ForeignKeyConstraint(['other_id_1', 'other_id_2'],
                                   ['some_table.id_1', 'some_table.id_2'],
                                   name='fk_test_name'),
              mysql_engine='InnoDB')

        Table('some_table', m2,
              Column('id_1', String(10), primary_key=True),
              Column('id_2', String(10), primary_key=True),
              mysql_engine='InnoDB')

        Table('user', m2,
              Column('id', Integer, primary_key=True),
              Column('name', String(50), nullable=False),
              Column('a1', String(10), server_default="x"),
              Column('other_id_1', String(10)),
              Column('other_id_2', String(10)),
              mysql_engine='InnoDB')

        diffs = self._fixture(m1, m2)

        self._assert_fk_diff(
            diffs[0], "remove_fk",
            "user", ['other_id_1', 'other_id_2'],
            "some_table", ['id_1', 'id_2'],
            conditional_name="fk_test_name"
        )

    def test_add_fk_colkeys(self):
        m1 = MetaData()
        m2 = MetaData()

        Table('some_table', m1,
              Column('id_1', String(10), primary_key=True),
              Column('id_2', String(10), primary_key=True),
              mysql_engine='InnoDB')

        Table('user', m1,
              Column('id', Integer, primary_key=True),
              Column('other_id_1', String(10)),
              Column('other_id_2', String(10)),
              mysql_engine='InnoDB')

        Table('some_table', m2,
              Column('id_1', String(10), key='tid1', primary_key=True),
              Column('id_2', String(10), key='tid2', primary_key=True),
              mysql_engine='InnoDB')

        Table('user', m2,
              Column('id', Integer, primary_key=True),
              Column('other_id_1', String(10), key='oid1'),
              Column('other_id_2', String(10), key='oid2'),
              ForeignKeyConstraint(['oid1', 'oid2'],
                                   ['some_table.tid1', 'some_table.tid2'],
                                   name='fk_test_name'),
              mysql_engine='InnoDB')

        diffs = self._fixture(m1, m2)

        self._assert_fk_diff(
            diffs[0], "add_fk",
            "user", ['other_id_1', 'other_id_2'],
            'some_table', ['id_1', 'id_2'],
            name="fk_test_name"
        )

    def test_no_change_colkeys(self):
        m1 = MetaData()
        m2 = MetaData()

        Table('some_table', m1,
              Column('id_1', String(10), primary_key=True),
              Column('id_2', String(10), primary_key=True),
              mysql_engine='InnoDB')

        Table('user', m1,
              Column('id', Integer, primary_key=True),
              Column('other_id_1', String(10)),
              Column('other_id_2', String(10)),
              ForeignKeyConstraint(['other_id_1', 'other_id_2'],
                                   ['some_table.id_1', 'some_table.id_2']),
              mysql_engine='InnoDB')

        Table('some_table', m2,
              Column('id_1', String(10), key='tid1', primary_key=True),
              Column('id_2', String(10), key='tid2', primary_key=True),
              mysql_engine='InnoDB')

        Table('user', m2,
              Column('id', Integer, primary_key=True),
              Column('other_id_1', String(10), key='oid1'),
              Column('other_id_2', String(10), key='oid2'),
              ForeignKeyConstraint(['oid1', 'oid2'],
                                   ['some_table.tid1', 'some_table.tid2']),
              mysql_engine='InnoDB')

        diffs = self._fixture(m1, m2)

        eq_(diffs, [])


class IncludeHooksTest(AutogenFixtureTest, TestBase):
    __backend__ = True
    __requires__ = 'fk_names',

    @config.requirements.no_name_normalize
    def test_remove_connection_fk(self):
        m1 = MetaData()
        m2 = MetaData()

        ref = Table(
            'ref', m1, Column('id', Integer, primary_key=True),
            mysql_engine='InnoDB')
        t1 = Table(
            't', m1, Column('x', Integer), Column('y', Integer),
            mysql_engine='InnoDB')
        t1.append_constraint(
            ForeignKeyConstraint([t1.c.x], [ref.c.id], name="fk1")
        )
        t1.append_constraint(
            ForeignKeyConstraint([t1.c.y], [ref.c.id], name="fk2")
        )

        ref = Table(
            'ref', m2, Column('id', Integer, primary_key=True),
            mysql_engine='InnoDB')
        Table(
            't', m2, Column('x', Integer), Column('y', Integer),
            mysql_engine='InnoDB')

        def include_object(object_, name, type_, reflected, compare_to):
            return not (
                isinstance(object_, ForeignKeyConstraint) and
                type_ == 'foreign_key_constraint'
                and reflected and name == 'fk1')

        diffs = self._fixture(m1, m2, object_filters=include_object)

        self._assert_fk_diff(
            diffs[0], "remove_fk",
            't', ['y'], 'ref', ['id'],
            conditional_name='fk2'
        )
        eq_(len(diffs), 1)

    def test_add_metadata_fk(self):
        m1 = MetaData()
        m2 = MetaData()

        Table(
            'ref', m1,
            Column('id', Integer, primary_key=True), mysql_engine='InnoDB')
        Table(
            't', m1,
            Column('x', Integer), Column('y', Integer), mysql_engine='InnoDB')

        ref = Table(
            'ref', m2, Column('id', Integer, primary_key=True),
            mysql_engine='InnoDB')
        t2 = Table(
            't', m2, Column('x', Integer), Column('y', Integer),
            mysql_engine='InnoDB')
        t2.append_constraint(
            ForeignKeyConstraint([t2.c.x], [ref.c.id], name="fk1")
        )
        t2.append_constraint(
            ForeignKeyConstraint([t2.c.y], [ref.c.id], name="fk2")
        )

        def include_object(object_, name, type_, reflected, compare_to):
            return not (
                isinstance(object_, ForeignKeyConstraint) and
                type_ == 'foreign_key_constraint'
                and not reflected and name == 'fk1')

        diffs = self._fixture(m1, m2, object_filters=include_object)

        self._assert_fk_diff(
            diffs[0], "add_fk",
            't', ['y'], 'ref', ['id'],
            name='fk2'
        )
        eq_(len(diffs), 1)

    @config.requirements.no_name_normalize
    def test_change_fk(self):
        m1 = MetaData()
        m2 = MetaData()

        r1a = Table(
            'ref_a', m1,
            Column('a', Integer, primary_key=True),
            mysql_engine='InnoDB'
        )
        Table(
            'ref_b', m1,
            Column('a', Integer, primary_key=True),
            Column('b', Integer, primary_key=True),
            mysql_engine='InnoDB'
        )
        t1 = Table(
            't', m1, Column('x', Integer),
            Column('y', Integer), Column('z', Integer),
            mysql_engine='InnoDB')
        t1.append_constraint(
            ForeignKeyConstraint([t1.c.x], [r1a.c.a], name="fk1")
        )
        t1.append_constraint(
            ForeignKeyConstraint([t1.c.y], [r1a.c.a], name="fk2")
        )

        Table(
            'ref_a', m2,
            Column('a', Integer, primary_key=True),
            mysql_engine='InnoDB'
        )
        r2b = Table(
            'ref_b', m2,
            Column('a', Integer, primary_key=True),
            Column('b', Integer, primary_key=True),
            mysql_engine='InnoDB'
        )
        t2 = Table(
            't', m2, Column('x', Integer),
            Column('y', Integer), Column('z', Integer),
            mysql_engine='InnoDB')
        t2.append_constraint(
            ForeignKeyConstraint(
                [t2.c.x, t2.c.z], [r2b.c.a, r2b.c.b], name="fk1")
        )
        t2.append_constraint(
            ForeignKeyConstraint(
                [t2.c.y, t2.c.z], [r2b.c.a, r2b.c.b], name="fk2")
        )

        def include_object(object_, name, type_, reflected, compare_to):
            return not (
                isinstance(object_, ForeignKeyConstraint) and
                type_ == 'foreign_key_constraint'
                and name == 'fk1'
            )

        diffs = self._fixture(m1, m2, object_filters=include_object)

        self._assert_fk_diff(
            diffs[0], "remove_fk",
            't', ['y'], 'ref_a', ['a'],
            name='fk2'
        )
        self._assert_fk_diff(
            diffs[1], "add_fk",
            't', ['y', 'z'], 'ref_b', ['a', 'b'],
            name='fk2'
        )
        eq_(len(diffs), 2)


class AutogenerateFKOptionsTest(AutogenFixtureTest, TestBase):
    __backend__ = True
    __requires__ = ('sqlalchemy_09', 'flexible_fk_cascades')

    def _fk_opts_fixture(self, old_opts, new_opts):
        m1 = MetaData()
        m2 = MetaData()

        Table('some_table', m1,
              Column('id', Integer, primary_key=True),
              Column('test', String(10)),
              mysql_engine='InnoDB')

        Table('user', m1,
              Column('id', Integer, primary_key=True),
              Column('name', String(50), nullable=False),
              Column('tid', Integer),
              ForeignKeyConstraint(['tid'], ['some_table.id'], **old_opts),
              mysql_engine='InnoDB')

        Table('some_table', m2,
              Column('id', Integer, primary_key=True),
              Column('test', String(10)),
              mysql_engine='InnoDB')

        Table('user', m2,
              Column('id', Integer, primary_key=True),
              Column('name', String(50), nullable=False),
              Column('tid', Integer),
              ForeignKeyConstraint(['tid'], ['some_table.id'], **new_opts),
              mysql_engine='InnoDB')

        return self._fixture(m1, m2)

    def _expect_opts_supported(self, deferrable=False, initially=False):
        if not config.requirements.reflects_fk_options.enabled:
            return False

        if deferrable and not config.requirements.fk_deferrable.enabled:
            return False

        if initially and not config.requirements.fk_initially.enabled:
            return False

        return True

    def test_add_ondelete(self):
        diffs = self._fk_opts_fixture(
            {}, {"ondelete": "cascade"}
        )

        if self._expect_opts_supported():
            self._assert_fk_diff(
                diffs[0], "remove_fk",
                "user", ["tid"],
                "some_table", ["id"],
                ondelete=None,
                conditional_name="servergenerated"
            )

            self._assert_fk_diff(
                diffs[1], "add_fk",
                "user", ["tid"],
                "some_table", ["id"],
                ondelete="cascade"
            )
        else:
            eq_(diffs, [])

    def test_remove_ondelete(self):
        diffs = self._fk_opts_fixture(
            {"ondelete": "CASCADE"}, {}
        )

        if self._expect_opts_supported():
            self._assert_fk_diff(
                diffs[0], "remove_fk",
                "user", ["tid"],
                "some_table", ["id"],
                ondelete="CASCADE",
                conditional_name="servergenerated"
            )

            self._assert_fk_diff(
                diffs[1], "add_fk",
                "user", ["tid"],
                "some_table", ["id"],
                ondelete=None
            )
        else:
            eq_(diffs, [])

    def test_nochange_ondelete(self):
        """test case sensitivity"""
        diffs = self._fk_opts_fixture(
            {"ondelete": "caSCAde"}, {"ondelete": "CasCade"}
        )
        eq_(diffs, [])

    def test_add_onupdate(self):
        diffs = self._fk_opts_fixture(
            {}, {"onupdate": "cascade"}
        )

        if self._expect_opts_supported():
            self._assert_fk_diff(
                diffs[0], "remove_fk",
                "user", ["tid"],
                "some_table", ["id"],
                onupdate=None,
                conditional_name="servergenerated"
            )

            self._assert_fk_diff(
                diffs[1], "add_fk",
                "user", ["tid"],
                "some_table", ["id"],
                onupdate="cascade"
            )
        else:
            eq_(diffs, [])

    def test_remove_onupdate(self):
        diffs = self._fk_opts_fixture(
            {"onupdate": "CASCADE"}, {}
        )

        if self._expect_opts_supported():
            self._assert_fk_diff(
                diffs[0], "remove_fk",
                "user", ["tid"],
                "some_table", ["id"],
                onupdate="CASCADE",
                conditional_name="servergenerated"
            )

            self._assert_fk_diff(
                diffs[1], "add_fk",
                "user", ["tid"],
                "some_table", ["id"],
                onupdate=None
            )
        else:
            eq_(diffs, [])

    def test_nochange_onupdate(self):
        """test case sensitivity"""
        diffs = self._fk_opts_fixture(
            {"onupdate": "caSCAde"}, {"onupdate": "CasCade"}
        )
        eq_(diffs, [])

    def test_nochange_ondelete_restrict(self):
        """test the RESTRICT option which MySQL doesn't report on"""

        diffs = self._fk_opts_fixture(
            {"ondelete": "restrict"}, {"ondelete": "restrict"}
        )
        eq_(diffs, [])

    def test_nochange_onupdate_restrict(self):
        """test the RESTRICT option which MySQL doesn't report on"""

        diffs = self._fk_opts_fixture(
            {"onupdate": "restrict"}, {"onupdate": "restrict"}
        )
        eq_(diffs, [])

    def test_nochange_ondelete_noaction(self):
        """test the NO ACTION option which generally comes back as None"""

        diffs = self._fk_opts_fixture(
            {"ondelete": "no action"}, {"ondelete": "no action"}
        )
        eq_(diffs, [])

    def test_nochange_onupdate_noaction(self):
        """test the NO ACTION option which generally comes back as None"""

        diffs = self._fk_opts_fixture(
            {"onupdate": "no action"}, {"onupdate": "no action"}
        )
        eq_(diffs, [])

    def test_change_ondelete_from_restrict(self):
        """test the RESTRICT option which MySQL doesn't report on"""

        # note that this is impossible to detect if we change
        # from RESTRICT to NO ACTION on MySQL.
        diffs = self._fk_opts_fixture(
            {"ondelete": "restrict"}, {"ondelete": "cascade"}
        )
        if self._expect_opts_supported():
            self._assert_fk_diff(
                diffs[0], "remove_fk",
                "user", ["tid"],
                "some_table", ["id"],
                onupdate=None,
                ondelete=mock.ANY,  # MySQL reports None, PG reports RESTRICT
                conditional_name="servergenerated"
            )

            self._assert_fk_diff(
                diffs[1], "add_fk",
                "user", ["tid"],
                "some_table", ["id"],
                onupdate=None,
                ondelete="cascade"
            )
        else:
            eq_(diffs, [])

    def test_change_onupdate_from_restrict(self):
        """test the RESTRICT option which MySQL doesn't report on"""

        # note that this is impossible to detect if we change
        # from RESTRICT to NO ACTION on MySQL.
        diffs = self._fk_opts_fixture(
            {"onupdate": "restrict"}, {"onupdate": "cascade"}
        )
        if self._expect_opts_supported():
            self._assert_fk_diff(
                diffs[0], "remove_fk",
                "user", ["tid"],
                "some_table", ["id"],
                onupdate=mock.ANY,  # MySQL reports None, PG reports RESTRICT
                ondelete=None,
                conditional_name="servergenerated"
            )

            self._assert_fk_diff(
                diffs[1], "add_fk",
                "user", ["tid"],
                "some_table", ["id"],
                onupdate="cascade",
                ondelete=None
            )
        else:
            eq_(diffs, [])

    def test_ondelete_onupdate_combo(self):
        diffs = self._fk_opts_fixture(
            {"onupdate": "CASCADE", "ondelete": "SET NULL"},
            {"onupdate": "RESTRICT", "ondelete": "RESTRICT"}
        )

        if self._expect_opts_supported():
            self._assert_fk_diff(
                diffs[0], "remove_fk",
                "user", ["tid"],
                "some_table", ["id"],
                onupdate="CASCADE",
                ondelete="SET NULL",
                conditional_name="servergenerated"
            )

            self._assert_fk_diff(
                diffs[1], "add_fk",
                "user", ["tid"],
                "some_table", ["id"],
                onupdate="RESTRICT",
                ondelete="RESTRICT"
            )
        else:
            eq_(diffs, [])

    @config.requirements.fk_initially
    def test_add_initially_deferred(self):
        diffs = self._fk_opts_fixture(
            {}, {"initially": "deferred"}
        )

        self._assert_fk_diff(
            diffs[0], "remove_fk",
            "user", ["tid"],
            "some_table", ["id"],
            initially=None,
            conditional_name="servergenerated"
        )

        self._assert_fk_diff(
            diffs[1], "add_fk",
            "user", ["tid"],
            "some_table", ["id"],
            initially="deferred"
        )

    @config.requirements.fk_initially
    def test_remove_initially_deferred(self):
        diffs = self._fk_opts_fixture(
            {"initially": "deferred"}, {}
        )

        self._assert_fk_diff(
            diffs[0], "remove_fk",
            "user", ["tid"],
            "some_table", ["id"],
            initially="DEFERRED",
            deferrable=True,
            conditional_name="servergenerated"
        )

        self._assert_fk_diff(
            diffs[1], "add_fk",
            "user", ["tid"],
            "some_table", ["id"],
            initially=None
        )

    @config.requirements.fk_deferrable
    @config.requirements.fk_initially
    def test_add_initially_immediate_plus_deferrable(self):
        diffs = self._fk_opts_fixture(
            {}, {"initially": "immediate", "deferrable": True}
        )

        self._assert_fk_diff(
            diffs[0], "remove_fk",
            "user", ["tid"],
            "some_table", ["id"],
            initially=None,
            conditional_name="servergenerated"
        )

        self._assert_fk_diff(
            diffs[1], "add_fk",
            "user", ["tid"],
            "some_table", ["id"],
            initially="immediate",
            deferrable=True
        )

    @config.requirements.fk_deferrable
    @config.requirements.fk_initially
    def test_remove_initially_immediate_plus_deferrable(self):
        diffs = self._fk_opts_fixture(
            {"initially": "immediate", "deferrable": True}, {}
        )

        self._assert_fk_diff(
            diffs[0], "remove_fk",
            "user", ["tid"],
            "some_table", ["id"],
            initially=None,  # immediate is the default
            deferrable=True,
            conditional_name="servergenerated"
        )

        self._assert_fk_diff(
            diffs[1], "add_fk",
            "user", ["tid"],
            "some_table", ["id"],
            initially=None,
            deferrable=None
        )

    @config.requirements.fk_initially
    @config.requirements.fk_deferrable
    def test_add_initially_deferrable_nochange_one(self):
        diffs = self._fk_opts_fixture(
            {"deferrable": True, "initially": "immediate"},
            {"deferrable": True, "initially": "immediate"}
        )

        eq_(diffs, [])

    @config.requirements.fk_initially
    @config.requirements.fk_deferrable
    def test_add_initially_deferrable_nochange_two(self):
        diffs = self._fk_opts_fixture(
            {"deferrable": True, "initially": "deferred"},
            {"deferrable": True, "initially": "deferred"}
        )

        eq_(diffs, [])

    @config.requirements.fk_initially
    @config.requirements.fk_deferrable
    def test_add_initially_deferrable_nochange_three(self):
        diffs = self._fk_opts_fixture(
            {"deferrable": None, "initially": "deferred"},
            {"deferrable": None, "initially": "deferred"}
        )

        eq_(diffs, [])

    @config.requirements.fk_deferrable
    def test_add_deferrable(self):
        diffs = self._fk_opts_fixture(
            {}, {"deferrable": True}
        )

        self._assert_fk_diff(
            diffs[0], "remove_fk",
            "user", ["tid"],
            "some_table", ["id"],
            deferrable=None,
            conditional_name="servergenerated"
        )

        self._assert_fk_diff(
            diffs[1], "add_fk",
            "user", ["tid"],
            "some_table", ["id"],
            deferrable=True
        )

    @config.requirements.fk_deferrable
    def test_remove_deferrable(self):
        diffs = self._fk_opts_fixture(
            {"deferrable": True}, {}
        )

        self._assert_fk_diff(
            diffs[0], "remove_fk",
            "user", ["tid"],
            "some_table", ["id"],
            deferrable=True,
            conditional_name="servergenerated"
        )

        self._assert_fk_diff(
            diffs[1], "add_fk",
            "user", ["tid"],
            "some_table", ["id"],
            deferrable=None
        )

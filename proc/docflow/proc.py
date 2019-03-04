# -*- coding: utf-8 -*-
"""
Реализация сервисных функций при работе с документами
@author: V-Liderman
"""
import os
from datetime import datetime
import shell
import dbmodel as db
from sqlalchemy.sql import exists

#директория по умолчанию для работы приложения
__BASE_DIR = os.path.join(os.path.dirname(__file__), '..\\..')
#Инфраструктура запуска процедур
SHELL = shell.ProcShell(shell.SqlAlchemy, base_dir=__BASE_DIR, debug=True)

def create_assignment(asgn_type: str, asgn_to: str,
                      f_division: int,
                      date: datetime=None, need_date: datetime=None,
                      asgn_by: str=None,
                      asgn_status: str=None,
                      doc_id:int=None \
                      ) -> db.DD_Docs_Assignments:
    '''Создание автоназначения
    asgn_type: Тип назначения
    doc_id: PK документа, к которому относится назначение
    asgn_parent_id: PK родительского назначения
    asgn_to: кому назначено (имя пользователя)
    Возвращает: PK созданного назначения
    '''
    #0) Начальные проверки
    session = SHELL.data_adapter.session
    assert session, 'Ошибка инициализации адаптера'
    assert f_division, 'Не задано подразделение'
    assert asgn_type, 'Не задан тип назначения'
#    assert asgn_by, 'Не задан поручитель'
    assert asgn_to, 'Не задан исполнитель' #????
    if not date:
        date = datetime.now()

    #1) разрешаем тип назначения, получаем начальный статус
    try:
        doc_assign_type, contract_status = \
            session.query(db.DS_Docs_Assignment_Types.LINK, db.XpoState.MarkerValue)\
                   .outerjoin(db.XpoStateMachine)\
                   .outerjoin(db.XpoState, db.XpoStateMachine.XpoState )\
                   .filter(db.DS_Docs_Assignment_Types.C_Const==asgn_type)\
                   .first() #todo: one()

    except:
        raise ValueError('Неверный тип назначения')

    #2) Разрашаем имя пользователя
    try:
        user =  session.query(db.SD_Employers.LINK)\
                .filter(db.SD_Employers.C_UID==asgn_to)\
                .scalar()
    except:
        raise ValueError('Неверный id пользователя')
    #3) если передали id документа или родительского назначения проверяем чтобы не было не исполенных
    if doc_id:
        exist_asgn: db.DD_Docs_Assignments = \
            session.query(db.DD_Docs_Assignments)\
                   .filter(exists().\
                           where(db.DD_Docs_Assignments.F_Docs.LINK==doc_id,
                                 db.DD_Docs_Assignments.F_Docs_Assignment_Types.C_Const==asgn_type,
                                 db.DD_Docs_Assignments.B_Done==False))\
                   .one_or_none()
        if exist_asgn:
            return exist_asgn

    # 4) Создаем назначение
    assignment = db.DD_Docs_Assignments(F_Division=f_division, D_Date=date, \
                                        D_NeedToDo_Date=need_date, \
                                        F_Employers=user,
                                        F_Docs_Assignment_Types=doc_assign_type, \
                                        F_Contract_Status_Assignment=contract_status, \
                                        F_Docs=doc_id)
    session.add(assignment)
    session.commit()
    return assignment

create_assignment(asgn_type='DDAT_Act_Agree', asgn_to=r'COMPULINK\ilner-ivanov', f_division=20)

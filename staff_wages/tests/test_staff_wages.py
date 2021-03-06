# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo import fields
from datetime import datetime
from odoo.exceptions import UserError


class test_staff_wages(TransactionCase):

    def setUp(self):
        super(test_staff_wages, self).setUp()
        self.staff_wages = self.env.ref('staff_wages.staff_wages_lili')

    def test_normal_case(self):
        '''测试正常业务流程'''
        # 计提lili的工资
        self.staff_wages._total_amount_wage()
        self.staff_wages.staff_wages_accrued()
        self.assertTrue(self.staff_wages.voucher_id)

        #反计提
        self.staff_wages.voucher_id.voucher_done()
        self.staff_wages.staff_wages_unaccrued()
        self.staff_wages.staff_wages_accrued()

        # 再次调用方法不修改数据不生成修正凭证
        self.staff_wages.staff_wages_accrued()
        self.assertTrue(not self.staff_wages.change_voucher_id)

        # 修改lili的基本工资并重新计提
        for line in self.staff_wages.line_ids:
            line.change_social_security()
            line.basic_wage = 5000
        self.staff_wages._total_amount_wage()
        self.staff_wages.staff_wages_accrued()
        self.assertTrue(self.staff_wages.change_voucher_id)

        # 在工资表上增加人员并重新计提
        l_change_voucher = self.staff_wages.change_voucher_id
        l_line = self.env['wages.line'].create({'name': self.env.ref('staff.lili').id,
                                       'basic_wage': 5000,
                                       'basic_date': 22,
                                       'date_number': 23,
                                       'order_id': self.staff_wages.id,
                                       })
        l_line.change_wage_addhour()
        l_line.change_add_wage()
        self.staff_wages._total_amount_wage()
        self.staff_wages.staff_wages_accrued()
        self.assertTrue(self.staff_wages.change_voucher_id != l_change_voucher)

        # 审核工资单
        self.staff_wages.change_voucher_id.voucher_done()
        self.staff_wages._total_amount_wage()
        self.staff_wages.staff_wages_confirm()

        # 反审核工资单
        self.staff_wages.payment = self.env.ref('core.alipay')
        self.staff_wages.payment.balance = 1000000
        self.staff_wages.other_money_order.other_money_done()
        self.staff_wages.staff_wages_draft()

        #删除工资单
        self.staff_wages.unlink()

    def test_personal_tax_value(self):
        # 个人所得税超额累进税率的每一档
        amount_lines = [80000, 55000, 35000, 9000, 4500, 1500, 0]
        # 避免有扣除
        self.staff_wages.line_ids[0].date_number = 22
        for line in amount_lines:
            # 基本工资大于每档1元
            self.staff_wages.line_ids[0].basic_wage = line + 3500 + 1
            self.assertTrue(self.staff_wages.line_ids[0].personal_tax)

    def test_unlink(self):
        # 审核工资单
        self.staff_wages.staff_wages_confirm()
        with self.assertRaises(UserError):
            self.staff_wages.unlink()

    def test_create_voucher(self):
        #修改单据日期
        self.staff_wages.date = datetime.now()
        self.staff_wages.staff_wages_accrued()
        with self.assertRaises(UserError):
            self.staff_wages.staff_wages_accrued()

    def test_staff_wages_unaccrued(self):
        # #修改单据上的信息并审核
        self.staff_wages.staff_wages_accrued()
        for line in self.staff_wages.line_ids:
            line.basic_wage = 5000
        self.staff_wages.staff_wages_accrued()
        with self.assertRaises(UserError):
            self.staff_wages.staff_wages_unaccrued()

    def test_change_wage_addhour(self):
        for line in self.staff_wages.line_ids:
            line.date_number = 32
        with self.assertRaises(UserError):
            line.change_wage_addhour()














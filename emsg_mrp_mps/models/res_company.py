# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _
from odoo.tools.date_utils import start_of, end_of, add, subtract
from odoo.tools.misc import format_date


class Company(models.Model):
    _inherit = "res.company"

    def _get_manufacturing_period(self):
        self.ensure_one()
        return self._context.get('manufacturing_period', self.manufacturing_period)
    
    def _get_date_range(self, years=False):
        self.ensure_one()
        date_range = []
        manufacturing_period = self._get_manufacturing_period()
        if not years:
            years = 0
        first_day = start_of(subtract(fields.Date.today(), years=years),
                             manufacturing_period)
        for columns in range(self.manufacturing_period_to_display):
            last_day = end_of(first_day, manufacturing_period)
            date_range.append((first_day, last_day))
            first_day = add(last_day, days=1)
        return date_range

    def _date_range_to_str(self):
        date_range = self._get_date_range()
        dates_as_str = []
        lang = self.env.context.get('lang')
        manufacturing_period = self._get_manufacturing_period()
        
        for date_start, date_stop in date_range:
            if manufacturing_period == 'month':
                dates_as_str.append(format_date(self.env, date_start, date_format='MMM yyyy'))
            elif manufacturing_period == 'week':
                dates_as_str.append(_('Week %(week_num)s (%(start_date)s-%(end_date)s/%(month)s)',
                    week_num=format_date(self.env, date_start, date_format='w'),
                    start_date=format_date(self.env, date_start, date_format='d'),
                    end_date=format_date(self.env, date_stop, date_format='d'),
                    month=format_date(self.env, date_start, date_format='MMM')
                ))
            else:
                dates_as_str.append(format_date(self.env, date_start, date_format='MMM d'))
        return dates_as_str

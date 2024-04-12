# -*- coding: utf-8 -*-

from collections import defaultdict, namedtuple
from dateutil.relativedelta import relativedelta
from math import log10

from odoo import api, fields, models, _
from odoo.tools.date_utils import add, subtract
from odoo.tools.float_utils import float_round
from odoo.osv.expression import OR, AND
from collections import OrderedDict


class MrpGuestForecast(models.Model):
    _name = 'mrp.guest.forecast'
    _order = 'date'
    _description = 'Guest Forecast at Date'

    date = fields.Date('Date', required=True)
    gc_project_qty = fields.Float('GC Projection')
    gc_actual_qty = fields.Float('Wrin Des')

    def set_gc_project_qty(self, date_index, quantity):
        date_start, date_stop = self.env.company._get_date_range()[date_index]
        existing_forecast = self.env['mrp.guest.forecast'].search([
                ('date', '>=', date_start),('date', '<=', date_stop)])
        quantity = float(quantity)
        quantity_to_add = quantity - sum(existing_forecast.mapped('gc_project_qty'))
        if existing_forecast:
            new_qty = existing_forecast[0].gc_project_qty + quantity_to_add
            # new_qty = float_round(new_qty, precision_rounding=self.product_uom_id.rounding)
            existing_forecast[0].write({'gc_project_qty': new_qty})
        else:
            new_qty = quantity
            existing_forecast.create({
                'gc_actual_qty': 0,
                'date': date_stop,
                'gc_project_qty': new_qty,
            })
        # TODO: should only get planning product schedule
        for production_schedule in self.env['mrp.production.schedule'].search([]):
            existing_products = production_schedule.forecast_ids.filtered(lambda p: p.date >= date_start and p.date <= date_stop)
            if existing_products:
                if production_schedule.case_pack > 0.0:
                    new_forecast_qty = new_qty * production_schedule.upt_demand_qty / 1000 / production_schedule.case_pack
                    new_forecast_qty = float_round(new_forecast_qty, precision_rounding=production_schedule.product_uom_id.rounding)
                else:
                    new_forecast_qty = 0.0
                existing_products[0].write({'forecast_qty': new_forecast_qty})
            else:
                if production_schedule.case_pack > 0.0:
                    forecast_qty = quantity * production_schedule.upt_demand_qty / 1000 / production_schedule.case_pack
                    forecast_qty = float_round(forecast_qty, precision_rounding=production_schedule.product_uom_id.rounding)
                else:
                    forecast_qty = 0.0
                existing_products.create({
                    'forecast_qty': forecast_qty,
                    'date': date_stop,
                    'replenish_qty': 0,
                    'production_schedule_id': production_schedule.id
                })
        return True

    def set_gc_actual_qty(self, date_index, quantity):
        date_start, date_stop = self.env.company._get_date_range()[date_index]
        existing_forecast = self.env['mrp.guest.forecast'].search([
                ('date', '>=', date_start),('date', '<=', date_stop)])
        quantity = float(quantity)
        quantity_to_add = quantity - sum(existing_forecast.mapped('gc_actual_qty'))
        if existing_forecast:
            new_qty = existing_forecast[0].gc_actual_qty + quantity_to_add
            # new_qty = float_round(new_qty, precision_rounding=self.product_uom_id.rounding)
            existing_forecast[0].write({'gc_actual_qty': new_qty})
        else:
            existing_forecast.create({
                'gc_actual_qty': quantity,
                'date': date_stop,
                'gc_project_qty': 0,
            })
        return True


class MrpProductionSchedule(models.Model):
    _inherit = 'mrp.production.schedule'

    # gc_project_qty = fields.Float('GC Projection')
    # gc_actual_qty = fields.Float('Wrin Des')
    upt_demand_qty = fields.Float('UPT Demand')
    case_pack = fields.Float('Case Pack')
    case_per_pallet = fields.Integer('Case/Pallet')
    pallet_per_cont = fields.Integer('Pallet/Full Cont')
    cont_factor = fields.Integer('Suggested Pallets per Cont')


    def set_forecast_qty_extra(self, date_index, quantity, stock_days):
        """ Save the forecast quantity:

        params quantity: The new total forecasted quantity
        params date_index: The manufacturing period
        """
        # Get the last date of current period
        self.ensure_one()
        date_start, date_stop = self.company_id._get_date_range()[date_index]
        existing_forecast = self.forecast_ids.filtered(lambda f:
            f.date >= date_start and f.date <= date_stop)
        quantity = float_round(float(quantity), precision_rounding=self.product_uom_id.rounding)
        quantity_to_add = quantity - sum(existing_forecast.mapped('forecast_qty'))

        total_case_to_renew = self.cont_factor * self.case_per_pallet

        if existing_forecast:
            new_qty = existing_forecast[0].forecast_qty + quantity_to_add
            new_qty = float_round(new_qty, precision_rounding=self.product_uom_id.rounding)
            if stock_days < 25: # TODO: just temp code for demo
                existing_forecast[0].write({'forecast_qty': new_qty, 'replenish_qty': total_case_to_renew})
            else:
                existing_forecast[0].write({'forecast_qty': new_qty})
        else:
            if stock_days < 25:
                existing_forecast.create({
                    'forecast_qty': quantity,
                    'date': date_stop,
                    'replenish_qty': total_case_to_renew,
                    'production_schedule_id': self.id
                })
            else:
                existing_forecast.create({
                    'forecast_qty': quantity,
                    'date': date_stop,
                    'replenish_qty': 0,
                    'production_schedule_id': self.id
                })
        return True
    
    # def set_gc_project_qty(self, date_index, quantity):
        # self.ensure_one()
        # date_start, date_stop = self.company_id._get_date_range()[date_index]
        # existing_forecast = self.forecast_ids.filtered(lambda f:
            # f.date >= date_start and f.date <= date_stop)
        # quantity = float_round(float(quantity), precision_rounding=self.product_uom_id.rounding)
        # quantity_to_add = quantity - sum(existing_forecast.mapped('gc_project_qty'))
        # if existing_forecast:
            # new_qty = existing_forecast[0].gc_project_qty + quantity_to_add
            # new_qty = float_round(new_qty, precision_rounding=self.product_uom_id.rounding)
            # if self.case_pack > 0.0:
                # new_forecast_qty = new_qty * self.upt_demand_qty / 1000 / self.case_pack
                # new_forecast_qty = float_round(new_forecast_qty, precision_rounding=self.product_uom_id.rounding)
            # else:
                # new_forecast_qty = 0.0
            # existing_forecast[0].write({'gc_project_qty': new_qty, 'forecast_qty': new_forecast_qty})
        # else:
            # # TODO: optimize later, why odoo calculate new_qty so completedly?
            # if self.case_pack > 0.0:
                # forecast_qty = quantity * self.upt_demand_qty / 1000 / self.case_pack
                # forecast_qty = float_round(forecast_qty, precision_rounding=self.product_uom_id.rounding)
            # else:
                # forecast_qty = 0.0
            # existing_forecast.create({
                # 'gc_project_qty': quantity,
                # 'forecast_qty': forecast_qty,
                # 'date': date_stop,
                # 'replenish_qty': 0,
                # 'production_schedule_id': self.id
            # })
        # return True

    # def set_gc_actual_qty(self, date_index, quantity):
        # self.ensure_one()
        # date_start, date_stop = self.company_id._get_date_range()[date_index]
        # existing_forecast = self.forecast_ids.filtered(lambda f:
            # f.date >= date_start and f.date <= date_stop)
        # quantity = float_round(float(quantity), precision_rounding=self.product_uom_id.rounding)
        # quantity_to_add = quantity - sum(existing_forecast.mapped('gc_actual_qty'))
        # if existing_forecast:
            # new_qty = existing_forecast[0].gc_actual_qty + quantity_to_add
            # new_qty = float_round(new_qty, precision_rounding=self.product_uom_id.rounding)
            # existing_forecast[0].write({'gc_actual_qty': new_qty})
        # else:
            # existing_forecast.create({
                # 'gc_actual_qty': quantity,
                # 'date': date_stop,
                # 'replenish_qty': 0,
                # 'production_schedule_id': self.id
            # })
        # return True

    # def set_upt_demand_qty(self, date_index, quantity):
        # self.ensure_one()
        # date_start, date_stop = self.company_id._get_date_range()[date_index]
        # existing_forecast = self.forecast_ids.filtered(lambda f:
            # f.date >= date_start and f.date <= date_stop)
        # quantity = float_round(float(quantity), precision_rounding=self.product_uom_id.rounding)
        # quantity_to_add = quantity - sum(existing_forecast.mapped('upt_demand_qty'))
        # if existing_forecast:
            # new_qty = existing_forecast[0].upt_demand_qty + quantity_to_add
            # new_qty = float_round(new_qty, precision_rounding=self.product_uom_id.rounding)
            # new_forecast_qty = existing_forecast[0].gc_project_qty * new_qty / 1000 / existing_forecast[0].case_pack
            # new_forecast_qty = float_round(new_forecast_qty, precision_rounding=self.product_uom_id.rounding)
            # existing_forecast[0].write({'upt_demand_qty': new_qty, 'forecast_qty': new_forecast_qty})
        # else:
            # existing_forecast.create({
                # 'upt_demand_qty': quantity,
                # 'date': date_stop,
                # 'replenish_qty': 0,
                # 'production_schedule_id': self.id
            # })
        # return True

    # def set_case_pack(self, date_index, quantity):
        # self.ensure_one()
        # date_start, date_stop = self.company_id._get_date_range()[date_index]
        # existing_forecast = self.forecast_ids.filtered(lambda f:
            # f.date >= date_start and f.date <= date_stop)
        # quantity = float_round(float(quantity), precision_rounding=self.product_uom_id.rounding)
        # quantity_to_add = quantity - sum(existing_forecast.mapped('case_pack'))
        # if existing_forecast:
            # new_qty = existing_forecast[0].case_pack + quantity_to_add
            # new_qty = float_round(new_qty, precision_rounding=self.product_uom_id.rounding)
            # new_forecast_qty = new_qty > 0 and existing_forecast[0].gc_project_qty * existing_forecast[0].upt_demand_qty / 1000 / new_qty or 0.0
            # new_forecast_qty = float_round(new_forecast_qty, precision_rounding=self.product_uom_id.rounding)
            # existing_forecast[0].write({'case_pack': new_qty})
        # else:
            # existing_forecast.create({
                # 'case_pack': quantity,
                # 'date': date_stop,
                # 'replenish_qty': 0,
                # 'production_schedule_id': self.id
            # })
        # return True

    @api.model
    def get_mps_view_state(self, domain=False, offset=0, limit=False):
        mps_data = super(MrpProductionSchedule, self).get_mps_view_state(domain=domain, offset=offset, limit=limit)
        company_id = self.env.company
        date_range = company_id._get_date_range()
        guest_schedule_data = []
        for index, (date_start, date_stop) in enumerate(date_range):
            forecast_values = {}
            forecast_values['date_start'] = date_start
            forecast_values['date_stop'] = date_stop
            existing_forecasts = self.env['mrp.guest.forecast'].search([
                ('date', '>=', date_start),('date', '<=', date_stop)])
            if existing_forecasts:
                forecast_values['gc_project_qty'] = sum(existing_forecasts.mapped('gc_project_qty'))
                forecast_values['gc_actual_qty'] = sum(existing_forecasts.mapped('gc_actual_qty'))
            else:
                forecast_values['gc_actual_qty'] = 0.0
                forecast_values['gc_project_qty'] = 0.0
            guest_schedule_data.append(forecast_values)
        mps_data['guest_schedule_ids'] = guest_schedule_data
        
        # change manufacturing_period by context
        if self._context.get('manufacturing_period'):
            mps_data['manufacturing_period'] = 'day'
        
        return mps_data


    # TODO: OVERRIDE ALL FUNCTION
    def get_production_schedule_view_state(self):
        company_id = self.env.company
        date_range = company_id._get_date_range()
        date_range_year_minus_1 = company_id._get_date_range(years=1)
        date_range_year_minus_2 = company_id._get_date_range(years=2)

        # We need to get the schedule that impact the schedules in self. Since
        # the state is not saved, it needs to recompute the quantity to
        # replenish of finished products. It will modify the indirect
        # demand and replenish_qty of schedules in self.
        schedules_to_compute = self.env['mrp.production.schedule'].browse(self.get_impacted_schedule()) | self

        # Dependencies between schedules
        indirect_demand_trees = schedules_to_compute._get_indirect_demand_tree()

        indirect_ratio_mps = schedules_to_compute._get_indirect_demand_ratio_mps(indirect_demand_trees)

        # Get the schedules that do not depends from other in first position in
        # order to compute the schedule state only once.
        indirect_demand_order = schedules_to_compute._get_indirect_demand_order(indirect_demand_trees)
        indirect_demand_qty = defaultdict(float)
        incoming_qty, incoming_qty_done = self._get_incoming_qty(date_range)
        outgoing_qty, outgoing_qty_done = self._get_outgoing_qty(date_range)
        dummy, outgoing_qty_year_minus_1 = self._get_outgoing_qty(date_range_year_minus_1)
        dummy, outgoing_qty_year_minus_2 = self._get_outgoing_qty(date_range_year_minus_2)
        read_fields = [
            'forecast_target_qty',
            'min_to_replenish_qty',
            'max_to_replenish_qty',
            'upt_demand_qty',
            'case_pack',
            'product_id',
        ]
        if self.env.user.has_group('stock.group_stock_multi_warehouses'):
            read_fields.append('warehouse_id')
        if self.env.user.has_group('uom.group_uom'):
            read_fields.append('product_uom_id')
        production_schedule_states = schedules_to_compute.read(read_fields)
        production_schedule_states_by_id = {mps['id']: mps for mps in production_schedule_states}
        for production_schedule in indirect_demand_order:
            # Bypass if the schedule is only used in order to compute indirect
            # demand.
            rounding = production_schedule.product_id.uom_id.rounding
            lead_time = production_schedule._get_lead_times()
            # Ignore "Days to Supply Components" when set demand for components since it's normally taken care by the
            # components themselves
            lead_time_ignore_components = lead_time - production_schedule.bom_id.days_to_prepare_mo
            production_schedule_state = production_schedule_states_by_id[production_schedule['id']]
            if production_schedule in self:
                procurement_date = add(fields.Date.today(), days=lead_time)
                precision_digits = max(0, int(-(log10(production_schedule.product_uom_id.rounding))))
                production_schedule_state['precision_digits'] = precision_digits
                production_schedule_state['forecast_ids'] = []

            starting_inventory_qty = production_schedule.product_id.with_context(warehouse=production_schedule.warehouse_id.id).qty_available
            # QuangTV: Set default  ending_inventory_qty
            ending_inventory_qty = starting_inventory_qty
            
            if len(date_range):
                starting_inventory_qty -= incoming_qty_done.get((date_range[0], production_schedule.product_id, production_schedule.warehouse_id), 0.0)
                starting_inventory_qty += outgoing_qty_done.get((date_range[0], production_schedule.product_id, production_schedule.warehouse_id), 0.0)

            for index, (date_start, date_stop) in enumerate(date_range):
                forecast_values = {}
                key = ((date_start, date_stop), production_schedule.product_id, production_schedule.warehouse_id)
                key_y_1 = (date_range_year_minus_1[index], *key[1:])
                key_y_2 = (date_range_year_minus_2[index], *key[1:])
                existing_forecasts = production_schedule.forecast_ids.filtered(lambda p: p.date >= date_start and p.date <= date_stop)
                
                if production_schedule in self:
                    forecast_values['date_start'] = date_start
                    forecast_values['date_stop'] = date_stop
                    forecast_values['incoming_qty'] = float_round(incoming_qty.get(key, 0.0) + incoming_qty_done.get(key, 0.0), precision_rounding=rounding)
                    forecast_values['outgoing_qty'] = float_round(outgoing_qty.get(key, 0.0) + outgoing_qty_done.get(key, 0.0), precision_rounding=rounding)
                    forecast_values['outgoing_qty_year_minus_1'] = float_round(outgoing_qty_year_minus_1.get(key_y_1, 0.0), precision_rounding=rounding)
                    forecast_values['outgoing_qty_year_minus_2'] = float_round(outgoing_qty_year_minus_2.get(key_y_2, 0.0), precision_rounding=rounding)
                    if forecast_values['outgoing_qty'] > 0.0:
                        forecast_values['stock_days'] = float_round(starting_inventory_qty/forecast_values['outgoing_qty'], precision_rounding=rounding)
                    else:
                        forecast_values['stock_days'] = 0.0
                        
                forecast_values['indirect_demand_qty'] = float_round(indirect_demand_qty.get(key, 0.0), precision_rounding=rounding, rounding_method='UP')
                replenish_qty_updated = False
                if existing_forecasts:
                    forecast_values['forecast_qty'] = float_round(sum(existing_forecasts.mapped('forecast_qty')), precision_rounding=rounding)
                    forecast_values['replenish_qty'] = float_round(sum(existing_forecasts.mapped('replenish_qty')), precision_rounding=rounding)

                    # Check if the to replenish quantity has been manually set or
                    # if it needs to be computed.
                    replenish_qty_updated = any(existing_forecasts.mapped('replenish_qty_updated'))
                    forecast_values['replenish_qty_updated'] = replenish_qty_updated
                    # forecast_values['gc_project_qty'] = float_round(sum(existing_forecasts.mapped('gc_project_qty')), precision_rounding=rounding)
                    # forecast_values['gc_actual_qty'] = float_round(sum(existing_forecasts.mapped('gc_actual_qty')), precision_rounding=rounding)
                    # forecast_values['upt_demand_qty'] = float_round(sum(existing_forecasts.mapped('upt_demand_qty')), precision_rounding=rounding)
                    # forecast_values['case_pack'] = float_round(sum(existing_forecasts.mapped('case_pack')), precision_rounding=rounding)
                else:
                    forecast_values['forecast_qty'] = 0.0
                    # forecast_values['gc_project_qty'] = 0.0
                    # forecast_values['gc_actual_qty'] = 0.0
                    # forecast_values['upt_demand_qty'] = 0.0
                    # forecast_values['case_pack'] = 0.0

                if not replenish_qty_updated:
                    # replenish_qty = production_schedule._get_replenish_qty(starting_inventory_qty - forecast_values['forecast_qty'] - forecast_values['indirect_demand_qty'])
                    # forecast_values['replenish_qty'] = float_round(replenish_qty, precision_rounding=rounding)

                    total_case_to_renew = production_schedule.cont_factor * production_schedule.case_per_pallet
                    if production_schedule in self and forecast_values['stock_days'] > 0 and forecast_values['stock_days'] < 25:
                        forecast_values['replenish_qty'] = total_case_to_renew
                    else:
                        forecast_values['replenish_qty'] = 0

                    forecast_values['replenish_qty_updated'] = False

                forecast_values['starting_inventory_qty'] = float_round(starting_inventory_qty, precision_rounding=rounding)
                forecast_values['safety_stock_qty'] = float_round(starting_inventory_qty - forecast_values['forecast_qty'] - forecast_values['indirect_demand_qty'] + forecast_values['replenish_qty'], precision_rounding=rounding)
                
                # Quangtv: add state name 'ending_inventory_qty'
                forecast_values['ending_inventory_qty'] = ending_inventory_qty
                ending_inventory_qty = float_round(starting_inventory_qty + forecast_values.get('replenish_qty', 0) - forecast_values.get('outgoing_qty', 0), precision_rounding=rounding)
                
                if production_schedule in self:
                    production_schedule_state['forecast_ids'].append(forecast_values)
                starting_inventory_qty = forecast_values['safety_stock_qty']
                if not forecast_values['replenish_qty']:
                    continue
                # Set the indirect demand qty for children schedules.
                for (product, ratio) in indirect_ratio_mps[(production_schedule.warehouse_id, production_schedule.product_id)].items():
                    related_date = max(subtract(date_start, days=lead_time_ignore_components), fields.Date.today())
                    index = next(i for i, (dstart, dstop) in enumerate(date_range) if related_date <= dstart or (related_date >= dstart and related_date <= dstop))
                    related_key = (date_range[index], product, production_schedule.warehouse_id)
                    indirect_demand_qty[related_key] += ratio * forecast_values['replenish_qty']

            if production_schedule in self:
                # The state is computed after all because it needs the final
                # quantity to replenish.
                forecasts_state = production_schedule._get_forecasts_state(production_schedule_states_by_id, date_range, procurement_date)
                forecasts_state = forecasts_state[production_schedule.id]
                for index, forecast_state in enumerate(forecasts_state):
                    production_schedule_state['forecast_ids'][index].update(forecast_state)

                # The purpose is to hide indirect demand row if the schedule do not
                # depends from another.
                has_indirect_demand = any(forecast['indirect_demand_qty'] != 0 for forecast in production_schedule_state['forecast_ids'])
                production_schedule_state['has_indirect_demand'] = has_indirect_demand
            
            # change manufacturing_period by context
            if self._context.get('manufacturing_period'):
                production_schedule_state['manufacturing_period'] = self._context.get('manufacturing_period', 'day')
            
        return [production_schedule_states_by_id[_id] for _id in self.ids if _id in production_schedule_states_by_id]


class MrpProductForecast(models.Model):
    _inherit = 'mrp.product.forecast'

    # gc_project_qty = fields.Float('GC Projection')
    # gc_actual_qty = fields.Float('Wrin Des')
    # upt_demand_qty = fields.Float('UPT Demand')
    # case_pack = fields.Float('Case Pack')
    # case_per_pallet = fields.Integer('Case/Pallet')
    # stock_days = fields.Float('Stock Days')

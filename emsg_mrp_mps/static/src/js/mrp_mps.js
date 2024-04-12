/** @odoo-module */

import { MasterProductionScheduleModel } from "@mrp_mps/models/master_production_schedule_model";
import MpsLineComponent from "@mrp_mps/components/line";
import MainComponent from "@mrp_mps/components/main";
import { patch } from "@web/core/utils/patch";

import { useService, useBus } from "@web/core/utils/hooks";
import { formatFloat } from "@web/views/fields/formatters";

import { Component, useRef, onPatched } from "@odoo/owl";


export class MpsGuestLineComponent extends Component {

    setup() {
        this.actionService = useService("action");
        this.dialogService = useService("dialog");
        this.orm = useService("orm");
        this.model = this.env.model;
        this.gcprojectRow = useRef("gcprojectRow");
        this.gcactualRow = useRef("gcactualRow");
    }

    get guestSchedule() {
        return this.props.data;
    }

    get groups() {
        return this.props.groups;
    }

    formatFloat(value) {
        return formatFloat(value, { digits: [false, 2] }); /* TODO: load digits from where??? */
    }

    _onFocusInput(ev) {
        ev.target.select();
    }

    _onChangeGCProject(ev) {
        const dateIndex = parseInt(ev.target.dataset.date_index);
        const GCProjectQty = ev.target.value;
        if (GCProjectQty === "" || isNaN(GCProjectQty)) {
            ev.target.value = this.model._getOriginGuestValue(dateIndex, 'gc_project_qty');
        } else {
            const inputSelector = 'input[data-date_index="' + (dateIndex + 1) + '"]';
            const nextInput = this.gcprojectRow.el.querySelector(inputSelector);
            if (nextInput) {
                nextInput.select();
            }
            this.model._saveGCProject(dateIndex, GCProjectQty).then(() => {
                const inputSelector = 'input[data-date_index="' + (dateIndex + 1) + '"]';
                const nextInput = this.gcprojectRow.el.querySelector(inputSelector);
                if (nextInput) {
                    nextInput.select();
                }
            }, () => {
                ev.target.value = this.model._getOriginGuestValue(dateIndex, 'gc_project_qty');
            });
        }
    }

    _onChangeGCActual(ev) {
        const dateIndex = parseInt(ev.target.dataset.date_index);
        const GCActualQty = ev.target.value;
        if (GCActualQty === "" || isNaN(GCActualQty)) {
            ev.target.value = this.model._getOriginGuestValue(dateIndex, 'gc_actual_qty');
        } else {
            const inputSelector = 'input[data-date_index="' + (dateIndex + 1) + '"]';
            const nextInput = this.gcactualRow.el.querySelector(inputSelector);
            if (nextInput) {
                nextInput.select();
            }
            this.model._saveGCActual(dateIndex, GCActualQty).then(() => {
                const inputSelector = 'input[data-date_index="' + (dateIndex + 1) + '"]';
                const nextInput = this.gcactualRow.el.querySelector(inputSelector);
                if (nextInput) {
                    nextInput.select();
                }
            }, () => {
                ev.target.value = this.model._getOriginGuestValue(dateIndex, 'gc_actual_qty');
            });
        }
    }

}

MpsGuestLineComponent.template = 'emsg_mrp_mps.MpsGuestLineComponent';

patch(MasterProductionScheduleModel.prototype, {

    _saveForecastExtra(productionScheduleId, dateIndex, forecastQty, stockDays) {
        return this.mutex.exec(() => {
            this.orm.call(
                'mrp.production.schedule',
                'set_forecast_qty_extra',
                [productionScheduleId, dateIndex, forecastQty, stockDays],
            ).then(() => {
                return this.reload(productionScheduleId);
            });
        });
    },

    _saveGCProject(dateIndex, GCProjectQty) {
        return this.mutex.exec(() => {
            this.orm.call(
                'mrp.guest.forecast',
                'set_gc_project_qty',
                [[], dateIndex, GCProjectQty],
            ).then(() => {
                return this.load();
            });
        });
    },

    _saveGCActual(dateIndex, GCActualQty) {
        return this.mutex.exec(() => {
            this.orm.call(
                'mrp.guest.forecast',
                'set_gc_actual_qty',
                [[], dateIndex, GCActualQty],
            ).then(() => {
                return this.load();
            });
        });
    },

    /* _saveUptDemandQty(productionScheduleId, dateIndex, UptDemandQty) {
        return this.mutex.exec(() => {
            this.orm.call(
                'mrp.production.schedule',
                'set_upt_demand_qty',
                [productionScheduleId, dateIndex, UptDemandQty],
            ).then(() => {
                return this.reload(productionScheduleId);
            });
        });
    },

    _saveCasePack(productionScheduleId, dateIndex, CasePack) {
        return this.mutex.exec(() => {
            this.orm.call(
                'mrp.production.schedule',
                'set_case_pack',
                [productionScheduleId, dateIndex, CasePack],
            ).then(() => {
                return this.reload(productionScheduleId);
            });
        });
    } */

    _getOriginGuestValue(dateIndex, inputName) {
        return this.data.guest_schedule_ids[dateIndex][inputName];
    },

});


patch(MpsLineComponent.prototype, {
    setup() {
        super.setup(...arguments);
        // this.gcprojectRow = useRef("gcprojectRow");
        // this.gcactualRow = useRef("gcactualRow");
        // this.casepackRow = useRef("casepackRow");
        // this.uptdemandRow = useRef("uptdemandRow");
        this.stockdaysRow = useRef("stockdaysRow");
    },

    _onClickOpenMPSProductView(productId, productName) {
        console.log('asd');
        
        // const productionScheduleId = Number(ev.target.closest('.o_mps_content').dataset.id);
        

        this.actionService.doAction({
            // ...context,
            name: "MPS:" + productName,
            type: "ir.actions.client",
            target: "new",
            tag: "mrp_mps_client_action",
            domain: [["product_id", "in", [productId]]],
            context: {
                manufacturing_period: 'day'
            },
            
        });
    },

    _onChangeForecastTest(ev, productionScheduleId) {
        const dateIndex = parseInt(ev.target.dataset.date_index);
        const forecastQty = ev.target.value;
        if (forecastQty === "" || isNaN(forecastQty)) {
            ev.target.value = this.model._getOriginValue(productionScheduleId, dateIndex, 'forecast_qty');
        } else {
            const stockDays = this.model._getOriginValue(productionScheduleId, dateIndex, 'stock_days');;
            this.model._saveForecastExtra(productionScheduleId, dateIndex, forecastQty, stockDays).then(() => {
                const inputSelector = 'input[data-date_index="' + (dateIndex + 1) + '"]';
                const nextInput = this.forecastRow.el.querySelector(inputSelector);
                if (nextInput) {
                    nextInput.select();
                }
            }, () => {
                ev.target.value = this.model._getOriginValue(productionScheduleId, dateIndex, 'forecast_qty');
            });
        }
    },

    

    /* _onChangeGCProject(ev, productionScheduleId) {
        const dateIndex = parseInt(ev.target.dataset.date_index);
        const GCProjectQty = ev.target.value;
        if (GCProjectQty === "" || isNaN(GCProjectQty)) {
            ev.target.value = this.model._getOriginValue(productionScheduleId, dateIndex, 'gc_project_qty');
        } else {
            this.model._saveGCProject(productionScheduleId, dateIndex, GCProjectQty).then(() => {
                const inputSelector = 'input[data-date_index="' + (dateIndex + 1) + '"]';
                const nextInput = this.gcprojectRow.el.querySelector(inputSelector);
                if (nextInput) {
                    nextInput.select();
                }
            }, () => {
                ev.target.value = this.model._getOriginValue(productionScheduleId, dateIndex, 'gc_project_qty');
            });
        }
    }, */

    /* _onChangeGCActual(ev, productionScheduleId) {
        const dateIndex = parseInt(ev.target.dataset.date_index);
        const GCActualQty = ev.target.value;
        if (GCActualQty === "" || isNaN(GCActualQty)) {
            ev.target.value = this.model._getOriginValue(productionScheduleId, dateIndex, 'gc_actual_qty');
        } else {
            this.model._saveGCActual(productionScheduleId, dateIndex, GCActualQty).then(() => {
                const inputSelector = 'input[data-date_index="' + (dateIndex + 1) + '"]';
                const nextInput = this.gcactualRow.el.querySelector(inputSelector);
                if (nextInput) {
                    nextInput.select();
                }
            }, () => {
                ev.target.value = this.model._getOriginValue(productionScheduleId, dateIndex, 'gc_actual_qty');
            });
        }
    }, */

    /* _onChangeUptDemandQty(ev, productionScheduleId) {
        const dateIndex = parseInt(ev.target.dataset.date_index);
        const UptDemandQty = ev.target.value;
        if (UptDemandQty === "" || isNaN(UptDemandQty)) {
            ev.target.value = this.model._getOriginValue(productionScheduleId, dateIndex, 'upt_demand_qty');
        } else {
            this.model._saveUptDemandQty(productionScheduleId, dateIndex, UptDemandQty).then(() => {
                const inputSelector = 'input[data-date_index="' + (dateIndex + 1) + '"]';
                const nextInput = this.casepackRow.el.querySelector(inputSelector);
                if (nextInput) {
                    nextInput.select();
                }
            }, () => {
                ev.target.value = this.model._getOriginValue(productionScheduleId, dateIndex, 'upt_demand_qty');
            });
        }
    },

    _onChangeCasePack(ev, productionScheduleId) {
        const dateIndex = parseInt(ev.target.dataset.date_index);
        const CasePack = ev.target.value;
        if (CasePack === "" || isNaN(CasePack)) {
            ev.target.value = this.model._getOriginValue(productionScheduleId, dateIndex, 'case_pack');
        } else {
            this.model._saveCasePack(productionScheduleId, dateIndex, CasePack).then(() => {
                const inputSelector = 'input[data-date_index="' + (dateIndex + 1) + '"]';
                const nextInput = this.casepackRow.el.querySelector(inputSelector);
                if (nextInput) {
                    nextInput.select();
                }
            }, () => {
                ev.target.value = this.model._getOriginValue(productionScheduleId, dateIndex, 'case_pack');
            });
        }
    } */

});


patch(MainComponent.prototype, {
    setup() {
        super.setup(...arguments);
    },

    get guestlines() {
        return this.model.data.guest_schedule_ids;
    }

});

Object.assign(MainComponent.components, { MpsGuestLineComponent });


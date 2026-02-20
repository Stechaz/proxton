/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { Component, useState, onWillStart, onWillUpdateProps } from "@odoo/owl";
import { Field } from "@web/views/fields/field";
import { patch } from "@web/core/utils/patch";
import { formatDateTime, parseDateTime } from "@web/core/l10n/dates";

// Approval indicator component - shown on the left of the field
export class ApprovalIndicator extends Component {
    static template = "proxton.ApprovalIndicator";
    static props = {
        record: { type: Object },
        fieldName: { type: String },
        approvalSourceMethod: { type: [String, { value: false }], optional: true },
        approvalSourceField: { type: [String, { value: false }], optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.dialog = useService("dialog");
        this.notification = useService("notification");

        this.state = useState({
            isApproved: false,
            needsReapproval: false,
            approvedByName: false,
            approvalDate: false,
            loading: true,
        });

        this.sourceInfo = useState({
            model: null,
            resId: null,
            field: null,
        });

        onWillStart(async () => {
            await this.loadSourceInfo();
            await this.loadApprovalStatus();
        });

        onWillUpdateProps(async (nextProps) => {
            if (nextProps.record.data[nextProps.fieldName] !== this.props.record.data[this.props.fieldName]) {
                await this.loadSourceInfo();
                await this.loadApprovalStatus();
            }
        });
    }

    get modelName() {
        return this.sourceInfo.model || this.props.record.resModel;
    }

    get resId() {
        return this.sourceInfo.resId || this.props.record.resId;
    }

    get fieldName() {
        return this.sourceInfo.field || this.props.fieldName;
    }

    get currentValue() {
        const value = this.props.record.data[this.props.fieldName];
        if (!value) {
            return "";
        }
        // Handle Many2many/One2many fields (extract record IDs)
        if (value.records && Array.isArray(value.records)) {
            return value.records.map(r => r.resId);
        }
        // Handle array of IDs
        if (Array.isArray(value)) {
            return value;
        }
        return value;
    }

    async loadSourceInfo() {
        if (this.props.approvalSourceMethod && this.props.record.resId) {
            try {
                // Pass the source field name if provided (for universal method)
                const args = this.props.approvalSourceField
                    ? [[this.props.record.resId], this.props.approvalSourceField]
                    : [[this.props.record.resId]];
                const info = await this.orm.call(
                    this.props.record.resModel,
                    this.props.approvalSourceMethod,
                    args
                );
                if (info && info.source_model) {
                    this.sourceInfo.model = info.source_model;
                    this.sourceInfo.resId = info.source_res_id;
                    this.sourceInfo.field = info.source_field;
                }
            } catch (e) {
                console.error("Failed to load source info:", e);
            }
        }
    }

    async loadApprovalStatus() {
        if (!this.resId) {
            this.state.loading = false;
            return;
        }

        try {
            const info = await this.orm.call(
                "approval.field",
                "get_approval_info",
                [this.modelName, this.resId, this.fieldName, this.currentValue]
            );

            this.state.isApproved = info.is_approved;
            this.state.needsReapproval = info.needs_reapproval;
            this.state.approvedByName = info.approved_by_name;
            this.state.approvalDate = info.approval_date;
        } catch (e) {
            console.error("Failed to load approval status:", e);
        }
        this.state.loading = false;
    }

    get checkboxTitle() {
        if (!this.props.record.resId) {
            return _t("Najprv uložte záznam");
        }
        if (this.state.loading) {
            return _t("Načítavam...");
        }
        if (this.state.needsReapproval) {
            return _t("Obsah sa zmenil od posledného schválenia. Kliknite na potvrdenie schválenia.");
        }
        if (this.state.isApproved) {
            const formattedDate = this.state.approvalDate
                ? formatDateTime(parseDateTime(this.state.approvalDate))
                : "";
            return _t("Schválené: %(name)s\n%(date)s", {
                name: this.state.approvedByName,
                date: formattedDate,
            });
        }
        return _t("Kliknite na potvrdenie schválenia");
    }

    onApprovalClick(ev) {
        ev.preventDefault();
        ev.stopPropagation();

        if (this.state.loading || !this.resId) {
            return;
        }

        const message = this.state.needsReapproval
            ? _t("Obsah sa zmenil od posledného schválenia. Chcete schváliť aktuálny obsah?")
            : _t("Chcete schváliť tento obsah?");

        this.dialog.add(ConfirmationDialog, {
            title: _t("Potvrdiť schválenie"),
            body: message,
            confirm: async () => {
                await this.approveField();
            },
            cancel: () => {},
        });
    }

    async approveField() {
        try {
            await this.orm.call(
                "approval.field",
                "approve_field",
                [this.modelName, this.resId, this.fieldName, this.currentValue]
            );

            this.notification.add(_t("Obsah bol úspešne schválený"), {
                type: "success",
            });

            await this.loadApprovalStatus();
        } catch (e) {
            this.notification.add(_t("Nepodarilo sa schváliť obsah"), {
                type: "danger",
            });
            console.error("Nepodarilo sa schváliť obsah:", e);
        }
    }
}

// Patch the Field component to support approvable attribute
patch(Field.prototype, {
    setup() {
        super.setup(...arguments);

        // Check if field has approvable attribute in fieldInfo.attrs
        const attrs = this.props.fieldInfo?.attrs || {};
        this.isApprovable = attrs.approvable === "1" ||
                           attrs.approvable === "true" ||
                           attrs.approvable === true;
        this.approvalSourceMethod = attrs.approval_source_method || false;
        this.approvalSourceField = attrs.approval_source_field || false;
    },
});

// Add ApprovalIndicator to Field's components
Field.components = { ...Field.components, ApprovalIndicator };

// Override Field template
Field.template = "proxton.ApprovableField";

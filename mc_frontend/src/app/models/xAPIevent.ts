import StatementBase from 'src/app/models/xAPI/StatementBase';

export class XAPIevent {
    public data: { statement: StatementBase };
    public type: string;

    constructor(init?: Partial<XAPIevent>) {
        Object.assign(this, init);
    }

    getBubbles() {
    }

    preventBubbling() {
    }

    scheduleForExternal() {
    }
}

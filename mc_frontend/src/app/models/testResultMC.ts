import StatementBase from 'src/app/models/xAPI/StatementBase';

export class TestResultMC {
    public statement: StatementBase;
    public innerHTML: string;
    constructor(init?: Partial<TestResultMC>) {
        Object.assign(this, init);
    }
}

export class FrequencyItem {
    public values: string[];
    public phenomena: string[];
    public count: number;

    constructor(init?: Partial<FrequencyItem>) {
        Object.assign(this, init);
    }
}


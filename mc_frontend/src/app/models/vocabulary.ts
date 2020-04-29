export class Vocabulary {
    public hasFrequencyOrder: boolean;
    public possibleSubcounts: number[];
    public totalCount: number;
    constructor(init?: Partial<Vocabulary>) {
        Object.assign(this, init);
    }
}

export class Sentence {
    public id: number;
    public matching_degree: number;
    constructor(init?: Partial<Sentence>) {
        Object.assign(this, init);
    }
}


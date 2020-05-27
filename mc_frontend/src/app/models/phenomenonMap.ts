export class PhenomenonMapContent {
    translationValues: { [translationsKey: string]: string };
    translationObject: object;
    specificValues: { [specificValue: string]: number };

    constructor(init?: Partial<PhenomenonMapContent>) {
        Object.assign(this, init);
    }
}

export class PhenomenonMap {
    public dependency: PhenomenonMapContent;
    public feats: PhenomenonMapContent;
    public lemma: PhenomenonMapContent;
    public upostag: PhenomenonMapContent;

    constructor(init?: Partial<PhenomenonMap>) {
        Object.assign(this, init);
    }
}

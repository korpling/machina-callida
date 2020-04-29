import {CorpusMC} from './corpusMC';
import {ExerciseMC} from './exerciseMC';
import {MoodleExerciseType, PartOfSpeechValue, Phenomenon} from './enum';
import {FrequencyItem} from './frequencyItem';
import {ApplicationState} from './applicationState';
import {TextData} from './textData';
import {AnnisResponse} from './annisResponse';
import {NodeMC} from './nodeMC';
import {TestResultMC} from './testResultMC';
import StatementBase from './xAPI/StatementBase';
import Result from './xAPI/Result';
import Score from './xAPI/Score';
import {TextRange} from './textRange';
import {Citation} from './citation';

export default class MockMC {
    static apiResponseCorporaGet: object = {
        corpora: [new CorpusMC({
            author: 'author',
            source_urn: 'urn',
            title: 'title',
        })]
    };
    static apiResponseFrequencyAnalysisGet: FrequencyItem[] = [new FrequencyItem({
        phenomena: [Phenomenon.partOfSpeech.toString()],
        values: [PartOfSpeechValue.adjective.toString()]
    })];
    static apiResponseTextGet: AnnisResponse = new AnnisResponse({
        nodes: [new NodeMC({udep_lemma: 'lemma', annis_tok: 'tok'})],
        links: []
    });
    static applicationState: ApplicationState = new ApplicationState({
        currentSetup: new TextData({
            currentCorpus: new CorpusMC({citations: {}}),
            currentTextRange: new TextRange({start: ['1', '2'], end: ['1', '2']})
        }),
        mostRecentSetup: new TextData({annisResponse: new AnnisResponse({nodes: [new NodeMC()], links: []})}),
        exerciseList: [new ExerciseMC()]
    });
    static popoverController: any = {create: () => Promise.resolve({present: () => Promise.resolve()})};
    static testResults: { [exerciseIndex: number]: TestResultMC } = {
        20: new TestResultMC({
            statement: new StatementBase({result: new Result({score: new Score({scaled: 0, raw: 0})})})
        })
    };
    static toastController: any = {create: () => Promise.resolve({present: () => Promise.resolve()})};

    static addIframe(h5pIframeString: string, buttonClass: string = null): HTMLIFrameElement {
        const iframe: HTMLIFrameElement = document.createElement('iframe');
        iframe.setAttribute('id', h5pIframeString.slice(1));
        document.body.appendChild(iframe);
        if (buttonClass) {
            const button: HTMLButtonElement = iframe.contentWindow.document.createElement('button');
            button.classList.add(buttonClass.slice(1));
            iframe.contentWindow.document.body.appendChild(button);
        }
        return document.querySelector(h5pIframeString);
    }
}

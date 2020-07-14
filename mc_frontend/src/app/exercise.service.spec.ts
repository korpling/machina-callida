import {TestBed} from '@angular/core/testing';

import {ExerciseService} from './exercise.service';
import {APP_BASE_HREF} from '@angular/common';
import {HttpClientTestingModule} from '@angular/common/http/testing';
import {IonicStorageModule} from '@ionic/storage';
import {TranslateTestingModule} from './translate-testing/translate-testing.module';
import {ExercisePart} from './models/exercisePart';
import MockMC from './models/mockMC';
import {ApplicationState} from './models/applicationState';
import {AnnisResponse, ExerciseTypePath} from '../../openapi';
import {ExerciseType, MoodleExerciseType} from './models/enum';
import {ExerciseParams} from './models/exerciseParams';
import configMC from '../configMC';
import Spy = jasmine.Spy;

declare var H5PStandalone: any;

describe('ExerciseService', () => {
    let exerciseService: ExerciseService;
    beforeEach(() => {
        TestBed.configureTestingModule({
            imports: [
                HttpClientTestingModule,
                IonicStorageModule.forRoot(),
                TranslateTestingModule,
            ],
            providers: [
                {provide: APP_BASE_HREF, useValue: '/'},
            ],
        });
        exerciseService = TestBed.inject(ExerciseService);
    });

    it('should be created', () => {
        expect(exerciseService).toBeTruthy();
    });

    it('should create a GUID', () => {
        const guid: string = exerciseService.createGuid();
        expect(guid.length).toBe(36);
    });

    it('should create a new H5P standalone instance', (done) => {
        let h5pCreated = false;

        class MockH5P extends Promise<void> {
            constructor(el, h5pLocation, options, displayOptions) {
                super((resolve) => {
                    h5pCreated = true;
                    return resolve();
                });
            }
        }

        spyOn(H5PStandalone, 'H5P').and.returnValue(MockH5P);
        const promise: any = exerciseService.createH5Pstandalone(null, '', null, null);
        promise.resolve().then(() => {
            expect(h5pCreated).toBe(true);
            done();
        });
    });

    it('should download a Blob as file', () => {
        const blob: Blob = new Blob([]);
        const anchor: HTMLAnchorElement = document.createElement('a');
        anchor.addEventListener('click', (downloadEvent: MouseEvent) => {
            downloadEvent.preventDefault();
        });
        spyOn(document, 'createElement').and.returnValue(anchor);
        exerciseService.downloadBlobAsFile(blob, '');
        expect(document.createElement).toHaveBeenCalledTimes(1);
    });

    it('should download a H5P exercise', (done) => {
        const postSpy: Spy = spyOn(exerciseService.helperService, 'makePostRequest').and.callFake(() => Promise.resolve(new Blob()));
        const downloadSpy: Spy = spyOn(exerciseService, 'downloadBlobAsFile');
        exerciseService.corpusService.annisResponse = {exercise_id: ''};
        exerciseService.corpusService.currentSolutions = exerciseService.corpusService.annisResponse.solutions = [{
            target: {
                token_id: 1,
                sentence_id: 1
            }
        }];
        exerciseService.corpusService.exercise.type = ExerciseType.markWords;
        exerciseService.downloadH5Pexercise().then(() => {
            expect(downloadSpy).toHaveBeenCalledTimes(1);
            postSpy.and.callFake(() => Promise.reject());
            exerciseService.corpusService.exercise.type = ExerciseType.cloze;
            exerciseService.downloadH5Pexercise().then(() => {
            }, () => {
                expect(downloadSpy).toHaveBeenCalledTimes(1);
                done();
            });
        });
    });

    it('should get H5P elements', () => {
        const getSpy: Spy = spyOn(exerciseService, 'getH5PIframe').and.returnValue(null);
        expect(exerciseService.getH5Pelements('.nonExistingClass')).toBeFalsy();
        const iframe: HTMLIFrameElement = document.createElement('iframe');
        document.body.appendChild(iframe);
        getSpy.and.returnValue(iframe);
        const element: HTMLElement = exerciseService.getH5Pelements('body');
        expect(element).toBeTruthy();
        const nodeList: NodeList = exerciseService.getH5Pelements('head', true);
        expect(nodeList.length).toBe(1);
    });

    it('should initialize H5P', (done) => {
        let h5pCalled = false;
        spyOn(exerciseService, 'createH5Pstandalone').and.callFake(() => new Promise(resolve => {
            h5pCalled = true;
            return resolve();
        }));
        exerciseService.initH5P('', false).then(() => {
            expect(h5pCalled).toBe(true);
            done();
        });
    });

    it('should load an exercise', (done) => {
        const ar: AnnisResponse = {exercise_type: MoodleExerciseType.cloze.toString()};
        const getSpy: Spy = spyOn(exerciseService.helperService, 'makeGetRequest').and.returnValue(Promise.resolve(ar));
        const initSpy: Spy = spyOn(exerciseService, 'initH5P').and.returnValue(Promise.resolve());
        exerciseService.helperService.applicationState.next(
            exerciseService.helperService.deepCopy(MockMC.applicationState) as ApplicationState);
        let ep: ExerciseParams = {eid: 'eid'};
        exerciseService.loadExercise(ep).then(() => {
            expect(initSpy).toHaveBeenCalledTimes(1);
            getSpy.and.callFake(() => Promise.reject());
            exerciseService.loadExercise(ep).then(() => {
            }, () => {
                expect(initSpy).toHaveBeenCalledTimes(1);
                ep = {file: '', type: ''};
                exerciseService.loadExercise(ep).then(() => {
                    ep = {file: '', type: ExerciseTypePath.VocList};
                    exerciseService.loadExercise(ep).then(() => {
                        expect(initSpy).toHaveBeenCalledTimes(3);
                        done();
                    });
                });
            });
        });
    });

    it('should load H5P', (done) => {
        const initSpy: Spy = spyOn(exerciseService, 'initH5P').and.returnValue(Promise.resolve());
        exerciseService.corpusService.exercise.type = ExerciseType.markWords;
        exerciseService.loadH5P('').then(() => {
            expect(initSpy).toHaveBeenCalledTimes(1);
            done();
        });
    });

    it('should set the H5P download event handler', () => {
        const downloadSpy: Spy = spyOn(exerciseService, 'downloadH5Pexercise').and.returnValue(Promise.resolve());
        const iframe: HTMLIFrameElement = MockMC.addIframe(exerciseService.h5pIframeString, exerciseService.downloadButtonString);
        exerciseService.setH5PdownloadEventHandler();
        const downloadButton: HTMLButtonElement = exerciseService.getH5Pelements(exerciseService.downloadButtonString);
        downloadButton.click();
        downloadSpy.and.callFake(() => Promise.reject());
        downloadButton.click();
        expect(downloadSpy).toHaveBeenCalledTimes(2);
    });

    it('should set H5P event handlers', (done) => {
        const listElement: HTMLElement = document.createElement('ul');
        const embedElement: HTMLLIElement = document.createElement('li');
        listElement.appendChild(embedElement);
        const reuseButton: HTMLLIElement = document.createElement('li');
        listElement.appendChild(reuseButton);
        const input: HTMLInputElement = document.createElement('input');
        const getSpy: Spy = spyOn(exerciseService, 'getH5Pelements').withArgs(exerciseService.embedButtonString)
            .and.returnValue(embedElement);
        getSpy.withArgs(exerciseService.embedSizeInputString, true).and.returnValue([input]);
        getSpy.withArgs(exerciseService.reuseButtonString).and.returnValue(reuseButton);
        let downloadClicked = false;
        spyOn(exerciseService, 'updateEmbedUrl').and.callFake(() => {
            expect(downloadClicked).toBe(true);
            done();
        });
        spyOn(exerciseService, 'setH5PdownloadEventHandler').and.callFake(() => {
            downloadClicked = true;
            embedElement.click();
        });
        exerciseService.setH5PeventHandlers();
        reuseButton.click();
    });

    it('should set the current exercise index', () => {
        expect(exerciseService.currentExercisePartIndex).toBeFalsy();
        const exerciseName = 'ex';
        exerciseService.currentExerciseParts = [new ExercisePart({startIndex: 0}),
            new ExercisePart({startIndex: 2, exercises: ['', exerciseName]}), new ExercisePart({startIndex: 4})];
        exerciseService.currentExerciseIndex = 3;
        expect(exerciseService.currentExercisePartIndex).toBe(1);
        expect(exerciseService.currentExerciseIndex).toBe(3);
        expect(exerciseService.currentExerciseName).toBe(exerciseName);
        exerciseService.currentExerciseIndex = 1;
        expect(exerciseService.currentExerciseName).toBeFalsy();
    });

    it('should set the H5P URL', () => {
        const url = 'url';
        exerciseService.setH5Purl(url);
        expect(window.localStorage.getItem(configMC.localStorageKeyH5P)).toBe(url);
    });

    it('should update the embed URL', () => {
        const textarea: HTMLTextAreaElement = document.createElement('textarea');
        const inputs: HTMLInputElement[] = [document.createElement('input'), document.createElement('input')];
        const getSpy: Spy = spyOn(exerciseService, 'getH5Pelements')
            .withArgs(exerciseService.embedTextAreaString).and.returnValue(textarea);
        getSpy.withArgs(exerciseService.embedSizeInputString, true).and.returnValue(inputs);
        exerciseService.corpusService.annisResponse = {exercise_type: MoodleExerciseType.cloze.toString()};
        exerciseService.updateEmbedUrl();
        expect(textarea.innerHTML).toBeTruthy();
    });
});

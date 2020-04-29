import {TestBed} from '@angular/core/testing';

import {HelperService} from './helper.service';
import {IonicStorageModule} from '@ionic/storage';
import {TranslateTestingModule} from './translate-testing/translate-testing.module';
import {HttpClientTestingModule} from '@angular/common/http/testing';
import {TranslateHttpLoader} from '@ngx-translate/http-loader';
import {Observable, of, range} from 'rxjs';
import Spy = jasmine.Spy;
import {PartOfSpeechValue} from './models/enum';
import {NavController, ToastController} from '@ionic/angular';
import configMC from '../configMC';
import {AppRoutingModule} from './app-routing.module';
import {APP_BASE_HREF} from '@angular/common';
import {ApplicationState} from './models/applicationState';
import {take} from 'rxjs/operators';
import {HttpErrorResponse, HttpParams} from '@angular/common/http';
import MockMC from './models/mockMC';

describe('HelperService', () => {
    let helperService: HelperService;
    beforeEach(() => {
        TestBed.configureTestingModule({
            imports: [
                HttpClientTestingModule,
                IonicStorageModule.forRoot(),
                TranslateTestingModule,
                AppRoutingModule,
            ],
            providers: [
                {provide: APP_BASE_HREF, useValue: '/'},
            ],
        });
        helperService = TestBed.inject(HelperService);
    });

    it('should be created', () => {
        expect(helperService).toBeTruthy();
    });

    it('should test IE11 mode', () => {
        // @ts-ignore
        // tslint:disable-next-line:no-string-literal
        window['MSInputMethodContext'] = true;
        // tslint:disable-next-line:no-string-literal
        document['documentMode'] = true;
        const helperService2: HelperService = new HelperService(helperService.http, helperService.storage, helperService.translate);
        expect(helperService2.isIE11).toBe(true);
    });

    it('should create a translate loader', () => {
        const thl: TranslateHttpLoader = HelperService.createTranslateLoader(helperService.http);
        expect(thl.suffix).toBe('.json');
    });

    it('should shuffle an array', () => {
        const array: number[] = [0, 1];
        const firstNumberArray: number[] = [];
        range(0, 100).forEach(() => {
            firstNumberArray.push(HelperService.shuffle(array)[0]);
        });
        expect(firstNumberArray).toContain(1);
    });

    it('should create a deep copy', () => {
        expect(helperService.deepCopy(undefined)).toBe(undefined);
        const oldDate: Date = new Date(1);
        const newDate: Date = helperService.deepCopy(oldDate);
        newDate.setTime(10000);
        expect(oldDate.getTime()).toBe(1);
        const oldArray: number[] = [0];
        const newArray: number[] = helperService.deepCopy(oldArray);
        newArray[0] = 1;
        expect(oldArray[0]).toBe(0);
        const oldObject: any = {unchanged: true};
        const newObject: any = helperService.deepCopy(oldObject);
        newObject.unchanged = false;
        expect(oldObject.unchanged).toBe(true);
    });

    it('should get a delayed translation', (done) => {
        const key = 'TEST';
        let translateSpy: Spy;
        helperService.getDelayedTranslation(helperService.translate, key).then((value: string) => {
            expect(value).toBe(key);
            translateSpy.and.returnValue(of(key.toLowerCase()));
            helperService.getDelayedTranslation(helperService.translate, key).then((newValue: string) => {
                expect(newValue).toBe(key.toLowerCase());
                done();
            });
        });
        translateSpy = spyOn(helperService.translate, 'get').and.returnValue(of(key));
    });

    it('should get enum values', () => {
        const enumValues: string[] = helperService.getEnumValues(PartOfSpeechValue);
        enumValues.forEach((ev: string) => expect(PartOfSpeechValue[ev]).toBeTruthy());
        expect(enumValues.length).toBe(7);
    });

    it('should go to a specific page', (done) => {
        function checkNavigation(navFunctions: any[], pageUrls: string[], navController: NavController, navSpy: Spy): Promise<void> {
            return new Promise<void>(resolve => {
                range(0, navFunctions.length).forEach(async (idx: number) => {
                    await navFunctions[idx](navController);
                    expect(navSpy).toHaveBeenCalledWith(pageUrls[idx]);
                });
                return resolve();
            });
        }

        const navCtrl: NavController = TestBed.inject(NavController);
        const forwardSpy: Spy = spyOn(navCtrl, 'navigateForward').and.returnValue(Promise.resolve(true));
        const navFnArr: any[] = [helperService.goToAuthorDetailPage, helperService.goToDocExercisesPage, helperService.goToDocSoftwarePage,
            helperService.goToDocVocUnitPage, helperService.goToExerciseListPage, helperService.goToExerciseParametersPage,
            helperService.goToImprintPage, helperService.goToInfoPage, helperService.goToPreviewPage, helperService.goToSourcesPage,
            helperService.goToTextRangePage, helperService.goToVocabularyCheckPage, helperService.goToKwicPage,
            helperService.goToRankingPage, helperService.goToSemanticsPage];
        const pageUrlArr: string[] = [configMC.pageUrlAuthorDetail, configMC.pageUrlDocExercises, configMC.pageUrlDocSoftware,
            configMC.pageUrlDocVocUnit, configMC.pageUrlExerciseList, configMC.pageUrlExerciseParameters, configMC.pageUrlImprint,
            configMC.pageUrlInfo, configMC.pageUrlPreview, configMC.pageUrlSources, configMC.pageUrlTextRange,
            configMC.pageUrlVocabularyCheck, configMC.pageUrlKwic, configMC.pageUrlRanking, configMC.pageUrlSemantics];
        checkNavigation(navFnArr, pageUrlArr, navCtrl, forwardSpy).then(async () => {
            await helperService.goToAuthorPage(navCtrl);
            expect(helperService.isVocabularyCheck).toBeFalsy();
            await helperService.goToShowTextPage(navCtrl, true);
            expect(helperService.isVocabularyCheck).toBe(true);
            const rootSpy: Spy = spyOn(navCtrl, 'navigateRoot').and.returnValue(Promise.resolve(true));
            await helperService.goToHomePage(navCtrl);
            expect(rootSpy).toHaveBeenCalledWith(configMC.pageUrlHome);
            helperService.goToTestPage(navCtrl).then(() => {
                expect(rootSpy).toHaveBeenCalledWith(configMC.pageUrlTest);
                done();
            });
        });
    });

    it('should initialize the application state', (done) => {
        function updateState(newState: ApplicationState): Promise<ApplicationState> {
            return new Promise<ApplicationState>(resolve => {
                helperService.applicationStateCache = null;
                helperService.initApplicationState();
                helperService.applicationState.pipe(take(1)).subscribe((state: ApplicationState) => {
                    resolve(state);
                });
            });
        }

        const localStorageSpy: Spy = spyOn(helperService.storage, 'get').withArgs(configMC.localStorageKeyApplicationState)
            .and.returnValue(Promise.resolve(JSON.stringify(new ApplicationState())));
        updateState(new ApplicationState()).then((state: ApplicationState) => {
            expect(state).toBeTruthy();
            localStorageSpy.and.returnValue(Promise.resolve(new ApplicationState({exerciseList: []})));
            updateState(new ApplicationState({exerciseList: []})).then((state2: ApplicationState) => {
                expect(state2.exerciseList.length).toBe(0);
                helperService.initApplicationState();
                helperService.applicationState.pipe(take(1)).subscribe((state3: ApplicationState) => {
                    expect(state3.exerciseList.length).toBe(0);
                    done();
                });
            });
        });
    });

    it('should make a get request', (done) => {
        const toastCtrl: ToastController = TestBed.inject(ToastController);
        spyOn(toastCtrl, 'create').and.returnValue(Promise.resolve({present: () => Promise.resolve()} as HTMLIonToastElement));
        const httpSpy: Spy = spyOn(helperService.http, 'get').and.returnValue(of(0));
        helperService.makeGetRequest(helperService.http, toastCtrl, '', new HttpParams()).then((result: number) => {
            expect(httpSpy).toHaveBeenCalledTimes(1);
            expect(result).toBe(0);
            httpSpy.and.returnValue(new Observable(subscriber => subscriber.error(new HttpErrorResponse({status: 500}))));
            helperService.makeGetRequest(helperService.http, toastCtrl, '', new HttpParams()).then(() => {
            }, (error: HttpErrorResponse) => {
                expect(error.status).toBe(500);
                done();
            });
        });
    });

    it('should make a post request', (done) => {
        const toastCtrl: ToastController = TestBed.inject(ToastController);
        spyOn(toastCtrl, 'create').and.returnValue(Promise.resolve({present: () => Promise.resolve()} as HTMLIonToastElement));
        const httpSpy: Spy = spyOn(helperService.http, 'post').and.returnValue(of(0));
        helperService.makePostRequest(helperService.http, toastCtrl, '', new FormData()).then((result: number) => {
            expect(httpSpy).toHaveBeenCalledTimes(1);
            expect(result).toBe(0);
            httpSpy.and.returnValue(new Observable(subscriber => subscriber.error(new HttpErrorResponse({status: 500}))));
            helperService.makePostRequest(helperService.http, toastCtrl, '', new FormData()).then(() => {
            }, (error: HttpErrorResponse) => {
                expect(error.status).toBe(500);
                done();
            });
        });
    });

    it('should save the application state', (done) => {
        helperService.saveApplicationState(helperService.deepCopy(MockMC.applicationState)).then(() => {
            helperService.storage.get(configMC.localStorageKeyApplicationState).then((jsonString: string) => {
                const state: ApplicationState = JSON.parse(jsonString) as ApplicationState;
                expect(state.mostRecentSetup.annisResponse.nodes.length).toBe(1);
                done();
            });
        });
    });
});

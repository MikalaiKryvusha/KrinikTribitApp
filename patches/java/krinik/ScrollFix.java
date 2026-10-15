package krinik;

import android.app.Activity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ScrollView;

import java.lang.reflect.Method;

/**
 * Patch 16 - every screen of the Tribit app scrolls when it does not fit (the owner, 2026-10-16: «они не скролятся у
 * них нихуя»). Called from BaseActivity.onCreate right after DataBinding has put the screen's root view into the
 * window. The wrap is posted to the root, so it runs after the screen's own afterCreate has set its adapters and
 * layout managers: if nothing in the screen scrolls VERTICALLY or must own the whole window, the root is moved into a
 * vertical ScrollView with fillViewport - a short screen looks exactly as before, a tall one scrolls. All 42 non-scrolling
 * own screens are DataBinding screens, which is why the wrap happens at run time: the binding keeps its root object
 * and type, only the root's parent changes.
 * Blocks the wrap: vertical scrollers (ScrollView, ListView, GridView, a RecyclerView whose layout manager scrolls
 * vertically or is not set yet, drawers, coordinators, refresh layouts), pagers, full-window surfaces (video, camera,
 * maps, Compose) and a WebView that fills its parent. Does not block: a horizontal RecyclerView (the EQ sliders) and a
 * WebView of fixed height (the EQ chart AAChartView) - seen blocking the EQ editor on the Titan 2026-10-16 01:14.
 * [TESTED: 2026-10-16 · Titan run testcases/reports/2026-10-16_fork_run2.md - the EQ editor root is a ScrollView by dumpsys]
 */
public final class ScrollFix {
    private static final String[] ALWAYS_BLOCK = {
        "ScrollView", "ListView", "GridView", "ViewPager", "RefreshLayout", "CoordinatorLayout", "DrawerLayout",
        "SurfaceView", "TextureView", "VideoView", "PlayerView", "ComposeView", "AndroidComposeView", "MapView",
        "CameraView", "PreviewView",
    };

    private ScrollFix() {}

    public static void wrap(final Activity activity, final View root) {
        if (root == null) return;
        root.post(new Runnable() {
            @Override
            public void run() {
                doWrap(activity, root);
            }
        });
    }

    private static void doWrap(Activity activity, View root) {
        try {
            if (activity.isFinishing() || !(root.getParent() instanceof ViewGroup) || blocks(root)) return;
            ViewGroup parent = (ViewGroup) root.getParent();
            int index = parent.indexOfChild(root);
            ViewGroup.LayoutParams params = root.getLayoutParams();
            parent.removeViewAt(index);
            ScrollView scroll = new ScrollView(activity);
            scroll.setFillViewport(true);
            scroll.setVerticalScrollBarEnabled(false);
            scroll.setOverScrollMode(View.OVER_SCROLL_IF_CONTENT_SCROLLS);
            scroll.addView(root, new ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
            parent.addView(scroll, index, params != null ? params
                    : new ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        } catch (RuntimeException ignored) {
            // A screen we did not foresee keeps its own layout: never crash the app over a scroll fix.
        }
    }

    private static boolean blocks(View view) {
        String chain = classChain(view);
        for (String name : ALWAYS_BLOCK) if (chain.contains("|" + name)) return true;
        if (chain.contains("|RecyclerView") && !scrollsOnlyHorizontally(view)) return true;
        if (chain.contains("|WebView") && fillsHeightToRoot(view)) return true;
        if (view instanceof ViewGroup) {
            ViewGroup group = (ViewGroup) view;
            for (int i = 0; i < group.getChildCount(); i++) if (blocks(group.getChildAt(i))) return true;
        }
        return false;
    }

    /**
     * True when the view and every ancestor up to the screen's content frame are MATCH_PARENT in height - a web view
     * that owns the screen. The EQ chart is MATCH_PARENT inside a 145 dp frame: not the screen's owner.
     */
    private static boolean fillsHeightToRoot(View view) {
        for (View v = view; v != null; v = v.getParent() instanceof View ? (View) v.getParent() : null) {
            if (v.getId() == android.R.id.content) return true;
            ViewGroup.LayoutParams lp = v.getLayoutParams();
            if (lp != null && lp.height != ViewGroup.LayoutParams.MATCH_PARENT) return false;
        }
        return true;
    }

    /** Simple names of the class and its superclasses, each prefixed with "|": "|AAChartView|WebView|...". */
    private static String classChain(View view) {
        StringBuilder sb = new StringBuilder();
        for (Class<?> c = view.getClass(); c != null && c != Object.class; c = c.getSuperclass()) {
            sb.append('|').append(c.getSimpleName());
        }
        return sb.toString();
    }

    /** True only for a RecyclerView whose layout manager is set and scrolls horizontally, not vertically. */
    private static boolean scrollsOnlyHorizontally(View recycler) {
        try {
            Method getLm = recycler.getClass().getMethod("getLayoutManager");
            Object lm = getLm.invoke(recycler);
            if (lm == null) return false;
            boolean vertical = (Boolean) lm.getClass().getMethod("canScrollVertically").invoke(lm);
            boolean horizontal = (Boolean) lm.getClass().getMethod("canScrollHorizontally").invoke(lm);
            return horizontal && !vertical;
        } catch (ReflectiveOperationException | RuntimeException e) {
            return false;
        }
    }
}
